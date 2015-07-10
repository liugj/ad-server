#!/usr/bin/env
# -*- coding: utf-8 -*-
import ConfigParser
import logging
from build_data import *
from process_file import file_process_t
import datetime

def create_valid_idea():
    global g_valid_idea_dict
    g_valid_idea_dict={}
    valid_user_dict={}
    valid_plan_dict={}
    plan_consume_dict={}   
    idea_consume_dict={}
    date_str=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    week_day=datetime.datetime.now().weekday()
    hour=int(datetime.datetime.now().strftime("%H"))
    hour_idx=str(week_day*24+hour)
    logging.debug("date:%s hour:%d hour_idx:%s" %(date_str,hour,hour_idx))
    #load user file
    user_file=g_conf.get("file","users")
    fp=open(user_file,"r")
    file_obj=file_process_t()   
    line_cnt=0
    for ori_line in fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            file_obj.init_header(data_list)
            continue
        user_id=file_obj.get_value("user_id",data_list) 
        consume=float(file_obj.get_value("consumption_total",data_list))
        total=float(file_obj.get_value("total",data_list))
        balance=total-consume
        if balance<=0:
            logging.debug("user id[%s] no budget" %(balance))
            continue
        valid_user_dict[user_id]=1
    fp.close()

    #load consumption
    consumption_file=g_conf.get("file","consumption")
    fp=open(consumption_file,"r")
    file_obj=file_process_t()   
    line_cnt=0
    for ori_line in fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            file_obj.init_header(data_list)
            continue
        plan_id=file_obj.get_value("plan_id",data_list)
        idea_id=file_obj.get_value("idea_id",data_list)
        consume=float(file_obj.get_value("price",data_list))
        if plan_id in plan_consume_dict:
            plan_consume_dict[plan_id]+=consume
        else:
            plan_consume_dict[plan_id]=consume
        if idea_id in idea_consume_dict:
            idea_consume_dict[idea_id]+=consume
        else:
            idea_consume_dict[idea_id]=consume
    fp.close()

    #create valid plan
    plan_file=g_conf.get("file","plans")
    fp=open(plan_file,"r")
    file_obj=file_process_t()   
    line_cnt=0
    for ori_line in fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            file_obj.init_header(data_list)
            continue
        plan_id=file_obj.get_value("plan_id",data_list)
        user_id=file_obj.get_value("user_id",data_list)
        budget=float(file_obj.get_value("budget",data_list))
        if not(user_id in valid_user_dict):
            logging.debug("plan id[%s] user id[%s] no budget" %(plan_id,user_id))
            continue
        if plan_id in plan_consume_dict:
            plan_consume=plan_consume_dict[plan_id]
        else:
            plan_consume=0
        if budget-plan_consume<=0:
            logging.debug("plan[%s] no budget" %(plan_id))
            continue
        valid_plan_dict[plan_id]=1
    fp.close()
        
    #create valid idea
    idea_file=g_conf.get("file","ideas")
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
        plan_id=file_obj.get_value("plan_id",data_list)
        budget=float(file_obj.get_value("budget",data_list))
        start_time=file_obj.get_value("start_time",data_list)
        end_time=file_obj.get_value("end_time",data_list)
        time_range_list=file_obj.get_value("timerange",data_list)
        if time_range_list!=None and time_range_list!="NULL" and len(time_range_list)>0:
            time_range_list=time_range_list.split(",")
            dict_temp={}
            for target_hour in time_range_list:
                dict_temp[target_hour]=1
            if not(hour_idx in dict_temp):
                logging.debug("hour idx[%s] not in hour range" %(hour_idx))
                continue
        if date_str<start_time or date_str>end_time:
            logging.debug("date not in date range idea_id[%s]" %(idea_id))
            continue
        if not(plan_id in valid_plan_dict):
            logging.debug("plan id[%s] no budget" %(plan_id))
            continue
        if idea_id in idea_consume_dict:
            idea_consume=idea_consume_dict[plan_id]
        else:
            idea_consume=0
        if budget-idea_consume<=0:
            logging.debug("idea id[%s] no budget" %(idea_id))
            continue
        g_valid_idea_dict[idea_id]=1
    fp.close()
            
def create_inverted_index():
    rdx_name_list=g_conf.get("ridx","ridx_list").split(",")
    for rdx_name in rdx_name_list:
        ridx_obj=inverted_index_t()
        name_list=rdx_name.split("_")
        for name in name_list:
            if name=="idea":
                continue
            key_name=name+"_id"
        data_file="../data/"+rdx_name+".txt"
        fp=open(data_file,"r")
        file_obj=file_process_t()   
        line_cnt=0
        indexed_idea_dict={}
        for ori_line in fp:
            data_list=ori_line.rstrip("\r\n").split("\t")
            line_cnt+=1
            if line_cnt==1:
                file_obj.init_header(data_list)
                continue
            idea_id=file_obj.get_value("idea_id",data_list) 
            if not(idea_id in g_valid_idea_dict):
                logging.debug("no need to indexed idea id[%s]" %(idea_id))
                continue
            key=file_obj.get_value(key_name,data_list)
            ridx_obj.insert_data(key,idea_id)
            indexed_idea_dict[idea_id]=1
        for idea_id in g_valid_idea_dict:
            if not(idea_id in indexed_idea_dict) and rdx_name!="ban_idea":
                ridx_obj.insert_data("0",idea_id)
        fp.close()
        ridx_obj.dump("../index/"+rdx_name+".ridx")    
               

def create_index():
    idea_fp=open(g_conf.get("file","ideas"),"r")
    index_name_list=g_conf.get("index","index_list").split(",")
    index_obj=index_t()
    line_cnt=0
    file_obj=file_process_t()   
    type_ridx=inverted_index_t()
    size_ridx=inverted_index_t()
    for ori_line in idea_fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            file_obj.init_header(data_list)
            continue
        idea_id=file_obj.get_value("id",data_list) 
        if not(idea_id in g_valid_idea_dict):
            logging.debug("idea id no budget[%s]" %(idea_id))
            continue
        type=file_obj.get_value("type",data_list)
        size_id=file_obj.get_value("size_id",data_list)
        type_ridx.insert_data(type,idea_id)
        size_ridx.insert_data(size_id,idea_id)
        for name in index_name_list:
            value=file_obj.get_value(name,data_list)
            index_obj.insert_data(idea_id,name,value)
    idea_fp.close()
    #dump type invert index
    type_ridx.dump("../index/type.ridx")
    size_ridx.dump("../index/size.ridx")
    file_obj=file_process_t()   
    line_cnt=0
    operate_fp=open(g_conf.get("file","idea_operate"),"r")
    for ori_line in operate_fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            file_obj.init_header(data_list)
            continue
        idea_id=file_obj.get_value("idea_id",data_list) 
        if not(idea_id in g_valid_idea_dict):
            logging.debug("idea id no budget[%s]" %(idea_id))
            continue
        value=file_obj.get_value("basic_bid",data_list)
        index_obj.insert_data(idea_id,"basic_bid",value)
    operate_fp.close()
    index_obj.dump(g_conf.get("index","idea_idx"))        


def init():
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S ',
                filename='../log/create_index.log',
                filemode='a')
    #init conf
    global g_conf
    global g_mysql
    g_conf=ConfigParser.ConfigParser()
    g_conf.read("../conf/create_index.conf")

if __name__=="__main__":
    init()
    create_valid_idea()
    create_inverted_index()
    create_index()
    
