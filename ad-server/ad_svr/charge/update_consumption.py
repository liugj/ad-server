#!/usr/bin/env
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import sys
import datetime
from process_file import file_process_t
g_conf=ConfigParser.ConfigParser()

def load_idea_info(idea_operator_file,idea_file):
    global g_idea_dict
    g_idea_dict={}
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


def process(input_file,output_file,date_str):
    input_fp=open(input_file,"r")
    output_fp=open(output_file,"w")
    date_time=datetime.datetime.strptime(date_str,"%Y-%m-%d-%H:%M:%S")
    date_day_str=datetime.datetime.strftime(date_time,"%Y-%m-%d")
    file_obj=file_process_t()
    line_cnt=0
    cost_dict={}
    price_dict={}
    for ori_line in input_fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            file_obj.init_header(data_list)
            continue
        idea_id=file_obj.get_value("idea_id",data_list)
        price=float(file_obj.get_value("price",data_list))
        cost=float(file_obj.get_value("cost",data_list))
        if idea_id in cost_dict:
            cost_dict[idea_id]+=cost
        else:
            cost_dict[idea_id]=cost
        if idea_id in price_dict:
            price_dict[idea_id]+=price
        else:
            price_dict[idea_id]=price
        
    output_fp.write("use mis;set names utf8;\n")
    for idea_id in cost_dict:
        cost=cost_dict[idea_id]
        if idea_id in price_dict:
            price=price_dict[idea_id]
        else:
            price=0
        if not(idea_id in g_idea_dict):
            logging.warning("no such idea id[%s] in idea lib" %(idea_id))
            continue
        idea_info_dict=g_idea_dict[idea_id]
        plan_id=idea_info_dict["plan_id"]
        user_id=idea_info_dict["user_id"]    
        output_fp.write("insert into consumptions(idea_id,user_id,plan_id,price,cost,date) values('%s','%s','%s','%f','%f','%s') on DUPLICATE KEY update price=price+%f,cost=cost+%f,user_id='%s',plan_id='%s';\n" %(idea_id,user_id,plan_id,price,cost,date_day_str,price,cost,user_id,plan_id))
        
    input_fp.close()
    output_fp.close()

def init():
    g_conf.read("../conf/update_consumption.conf")
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../log/update_consumption.log',
                filemode='a')

    load_idea_info(g_conf.get("file","idea_operate"),g_conf.get("file","idea"))

if __name__=="__main__":
    init()
    process(sys.argv[1],sys.argv[2],sys.argv[3])    
    

