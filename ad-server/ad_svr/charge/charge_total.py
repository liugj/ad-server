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
import json
from SSDB import SSDB

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

    
            

def charge(url,sql_fp,last_time_str):
    global g_ssdb_obj
    item_list=url.split("$$$")
    ad_action_dict={}
    for item in item_list:
        key_value_list=item.split("*")
        key=key_value_list[0]
        value=key_value_list[1]
        ad_action_dict[key]=value
    idea_id=ad_action_dict["idea_id"].rstrip(" ").rstrip("&")
    idea_info_dict=g_idea_dict[idea_id]
    charge_type=idea_info_dict["charge_type"]
    imp_id=ad_action_dict["id"]
    #charge_type=g_idea_dict[idea_id]["charge_type"]
    
    result_dict={"cost":0.0,"price":0.0,"idea_id":idea_id,"impid":imp_id,"charge_type":charge_type,"ad_action":ad_action_dict["type"]}
    if ad_action_dict["env"]=="test":
        logging.info("idea_id:%s env test" %(idea_id))
        return result_dict
    if ad_action_dict["type"]=="win_notice":
        win_price_coded=ad_action_dict["win_price"]
        win_cost_ori=g_decryter.TestWinningPrice(win_price_coded)
        win_cost=float(win_cost_ori)/10000000
        result_dict["cost"]=win_cost
        if charge_type=="cpm":
            result_dict["price"]=win_cost*(1+float(g_conf.get("para","default_profit")))
    elif ad_action_dict["type"]=="click" and charge_type=="cpc":
        result_dict["price"]=idea_info_dict["basic_price"]
    elif ad_action_dict["type"]=="open" and charge_type=="cpa":
        result_dict["price"]=idea_info_dict["basic_price"]
    elif ad_action_dict["type"]=="show":
        dpid=ad_action_dict["dpid"]
        key=dpid+"\001"+idea_id
        ret_list=str(g_ssdb_obj.request('incr', [key, '1'])).split(" ")
        if ret_list[0]!="ok":
            logging.warning("set values to ssdb failed[%s]" %(key))
    log_dict=result_dict.copy()
    log_dict["price"]*=1000
    log_dict["cost"]*=1000
    user_id=idea_info_dict["user_id"]
    plan_id=idea_info_dict["plan_id"]
    charge_type=idea_info_dict["charge_type"]
    if result_dict["cost"]>0:
        sql_fp.write("insert into charge_record(user_id,plan_id,idea_id,charge_time,cost,session_id,charge_type) values('%s','%s','%s','%s','%f','%s','%s') on DUPLICATE KEY update cost=cost+0;\n" %(user_id,plan_id,idea_id,last_time_str,result_dict["cost"],imp_id,charge_type))
        
    if result_dict["price"]>0:
       sql_fp.write("insert into charge_record(user_id,plan_id,idea_id,charge_time,price,session_id,charge_type) values('%s','%s','%s','%s','%f','%s','%s') on DUPLICATE KEY update price=price+(%f-price);\n" %(user_id,plan_id,idea_id,last_time_str,result_dict["price"],imp_id,charge_type,result_dict["price"]))

    return result_dict

def process_log(last_time_str,now_time_str,sql_file):
    pattern=re.compile(r'^(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\s-\s(.*)\s\[(.*)\]\s\"(.*)\"\s(\d{3,})\s(\d+)\s\"([^\s]*)\"\s\"(.*?)\"\s\"(.*)\"$')
    sql_fp=open(sql_file,"w")
    sql_fp.write("use mis;set names utf8;\n")
    last_time=datetime.datetime.strptime(last_time_str,"%Y-%m-%d-%H:%M:%S")
    now_time=datetime.datetime.strptime(now_time_str,"%Y-%m-%d-%H:%M:%S")

    file_prefix_list=[]
    #file_prefix=last_time.strftime("%Y%m%d%H")
    #file_prefix_list.append(file_prefix)
    minute=last_time.strftime("%M")
    file_list=[]
    if int(minute)<100:
        last_hour=int(last_time.strftime("%H"))-1
        file_prefix=last_time.strftime("%Y%m%d*")#+str(last_hour)
        #file_list=glob.glob(g_conf.get("log","nginx_log")+"/"+file_prefix+"*") 
        file_prefix_list.append(file_prefix)
    idea_charge_dict={}
    #for time_prefix in file_prefix_list:
    log_file_list=[]
    #print file_prefix_list
    log_file_list.append(g_conf.get("log","nginx_log")+"/"+"monitor.shoozen.net.access.log")
    for file_prefix in file_prefix_list:
        log_file_list+=glob.glob(g_conf.get("log","nginx_log")+"/"+file_prefix+"*monitor.shoozen*")
        
    for log_file in log_file_list:
            print log_file
            fp=open(log_file,"r")
            for line in fp:
                line=line.rstrip("\r\n")
                #print line
                try:
                    pattern2=re.compile(r"GET /track.gif\?(.*?)HTTP")
                    result=pattern.match(line)
                    ip=result.group(1)
                    url_ori=result.group(4)
                    url=pattern2.match(url_ori).group(1)
                    time_stamp_list=result.group(3).split(" ")
                    time_stamp_str=time_stamp_list[0]
                    time_datetime=datetime.datetime.strptime(time_stamp_str,"%d/%b/%Y:%H:%M:%S")
                except:
                    logging.warning("invalid line:%s" %(line))
                    continue   
                if time_datetime<last_time or time_datetime>now_time:
                    logging.debug("skip time:%s start time:%s end_time:%s" %(time_stamp_str,last_time_str,now_time_str))
                    continue
                ret_dict=charge(url,sql_fp,time_datetime)
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

def init():
    timestamp=datetime.datetime.now().strftime("%Y%m%d%H")
    g_conf.read("../conf/charge_python.conf")
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../charge_log/charge_python.'+timestamp+'.log',
                filemode='a')
    global g_idea_dict
    g_idea_dict={}
    load_idea_info(g_conf.get("file","idea_operate"),g_conf.get("file","idea"))
    global g_decryter
    g_decryter=ctypes.CDLL("./libdecrypter.so")
    global g_ssdb_obj
    g_ssdb_obj = SSDB(g_conf.get("ssdb","ip"),int(g_conf.get("ssdb","freq_control_port")))

if __name__=="__main__":
    init()
    last_time=sys.argv[1]
    now_time=sys.argv[2]
    sql_file=sys.argv[3]
    process_log(last_time,now_time,sql_file)
