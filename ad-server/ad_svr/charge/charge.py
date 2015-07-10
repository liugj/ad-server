#!/usr/bin/env
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import datetime
import sys
import types
import glob
import re
import os
g_conf=ConfigParser.ConfigParser()
from process_file import file_process_t
import ctypes

def load_idea_info(idea_operator_file,idea_file):
    fp=open(idea_operator_file,"r")
    file_obj=file_process_t()
    line_cnt=0
    for ori_line in fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            file_obj.init_header(data_list)
            continue
        idea_id=file_obj.get_value("idea_id",data_list)
        charge_type=file_obj.get_value("charge_type",data_list)
        basic_price=float(file_obj.get_value("basic_price",data_list))
        g_idea_dict[idea_id]={"charge_type":charge_type,"basic_price":basic_price}
    fp.close()   

    fp=open(idea_file,"r")
    file_obj=file_process_t()
    line_cnt=0
    for ori_line in fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            file_obj.init_header(data_list)
            continue
        idea_id=file_obj.get_value("id",data_list)
        user_id=file_obj.get_value("user_id",data_list)
        plan_id=file_obj.get_value("plan_id",data_list)
        if idea_id in g_idea_dict:
            g_idea_dict[idea_id]["user_id"]=user_id
            g_idea_dict[idea_id]["plan_id"]=plan_id
        else:
            sub_dict={}
            sub_dict={"user_id":user_id,"plan_id":plan_id,"charge_type":"cpm"}
            g_idea_dict[idea_id]=sub_dict
    fp.close()   

    
            

def charge(url):
    item_list=url.split("$$$")
    ad_action_dict={}
    for item in item_list:
        key_value_list=item.split("*")
        key=key_value_list[0]
        value=key_value_list[1]
        ad_action_dict[key]=value
    idea_id=ad_action_dict["idea_id"]
    idea_info_dict=g_idea_dict[idea_id]
    charge_type=idea_info_dict["charge_type"]
    #charge_type=g_idea_dict[idea_id]["charge_type"]
    
    result_dict={"cost":0.0,"price":0.0,"idea_id":idea_id}
    if ad_action_dict["type"]=="win_notice":
        win_price_coded=ad_action_dict["win_price"]
        win_cost_ori=g_decryter.TestWinningPrice(win_price_coded)
        win_cost=float(win_cost_ori)/10000000
        result_dict["cost"]=win_cost
        if charge_type=="cpm":
            result_dict["price"]=win_cost*(1+float(g_conf.get("para","default_profit")))
            
    elif ad_action_dict["type"]=="click" and charge_type=="click":
        result_dict["price"]=idea_info_dict["basic_price"]
    elif ad_action_dict["type"]=="open" and charge_type=="cpa":
        result_dict["price"]=idea_info_dict["basic_price"]
    return result_dict

def process_log(last_time_str,now_time_str,sql_file):
    pattern=re.compile(r'^(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\s-\s(.*)\s\[(.*)\]\s\"(.*)\"\s(\d{3,})\s(\d+)\s\"([^\s]*)\"\s\"(.*?)\"\s\"(.*)\"$')
    sql_fp=open(sql_file,"w")
    last_time=datetime.datetime.strptime(last_time_str,"%Y-%m-%d-%H:%M:%S")
    now_time=datetime.datetime.strptime(now_time_str,"%Y-%m-%d-%H:%M:%S")

    file_prefix_list=[]
    file_prefix=last_time.strftime("%Y%m%d%H")
    file_prefix_list.append(file_prefix)
    minute=last_time.strftime("%M")
    if int(minute)<5:
        last_hour=int(last_time.strftime("%H"))-1
        file_prefix=last_time.strftime("%Y%m%d")+str(last_hour)
        file_prefix_list.append(file_prefix)
    idea_charge_dict={}
    for time_prefix in file_prefix_list:
        file_list=glob.glob(g_conf.get("log","nginx_log")+"/"+time_prefix+"*") 
        for log_file in  file_list:
            logging.debug("process file:%s" %(log_file))
            fp=open(log_file,"r")
            for line in fp:
                line=line.rstrip("\r\n")
                #print line
                pattern2=re.compile(r"GET /track.gif\?(.*?)HTTP")
                result=pattern.match(line)
                ip=result.group(1)
                url_ori=result.group(4)
                url=pattern2.match(url_ori).group(1)
                time_stamp_list=result.group(3).split(" ")
                time_stamp_str=time_stamp_list[0]
                time_datetime=datetime.datetime.strptime(time_stamp_str,"%d/%b/%Y:%H:%M:%S")
                if time_datetime<last_time or time_datetime>now_time:
                    logging.debug("skip time:%s start time:%s end_time:%s" %(time_stamp_str,last_time_str,now_time_str))
                    continue
                ret_dict=charge(url)
                idea_id=ret_dict["idea_id"]         
                if idea_id in idea_charge_dict:
                    [cost,price]=idea_charge_dict[idea_id]
                    cost+=ret_dict["cost"]       
                    price+=ret_dict["price"]       
                else:
                    cost=ret_dict["cost"]       
                    price=ret_dict["price"]       
                idea_charge_dict[idea_id]=[cost,price]
    last_time_str=last_time.strftime("%Y-%m-%d")
    #create sql
    user_price_dict={}
    sql_fp.write("use mis;set names utf8;\n")
    for idea_id in  idea_charge_dict:
        user_id=g_idea_dict[idea_id]["user_id"]
        plan_id=g_idea_dict[idea_id]["plan_id"]
        [cost,price]=idea_charge_dict[idea_id]
        if user_id in user_price_dict:
            user_price_dict[user_id]+=price
        else:
            user_price_dict[user_id]=price
        sql_fp.write("insert into consumptions(user_id,plan_id,idea_id,price,date,updated_at) values('%s','%s','%s','%f','%s','%s');\n" %(user_id,plan_id,idea_id,price,last_time_str,last_time.strftime("%Y-%m-%d %H:%M:%S")))
                      
    for user_id in user_price_dict:
        price=user_price_dict[user_id]
        sql_fp.write("update basics set consumption_total=consumption_total+%f where id='%s';\n" %(price,user_id))       
def init():
    timestamp=datetime.datetime.now().strftime("%Y-%m-%d")
    g_conf.read("../conf/charge_python.conf")
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../log/charge_python.'+timestamp+'.log',
                filemode='a')
    global g_idea_dict
    g_idea_dict={}
    load_idea_info(g_conf.get("file","idea_operate"),g_conf.get("file","idea"))
    global g_decryter
    g_decryter=ctypes.CDLL("./libdecrypter.so")

if __name__=="__main__":
    init()
    last_time=sys.argv[1]
    now_time=sys.argv[2]
    sql_file=sys.argv[3]
    process_log(last_time,now_time,sql_file)
