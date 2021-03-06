#!/usr/bin/env
# -*- coding: utf-8 -*-
import sys
import ConfigParser
import logging
import csv
import gearman
import time
from gearman import GearmanClient
import multiprocessing
from multiprocessing import Process, Manager,Pool
import json
from gearman import GearmanClient
import msgpack
import datetime
from adx_id_map import adx_id_map
from adx_interface import adx_interface_t
from build_data import *
from ip_region_parse import ip_parse_t
from filter import filter_t
from rank_bid import rank_bid_t
from transform_id import transform_id_t
from predict import predict_model_t
from extract_feature import extract_feature_t
from idea_operate import idea_operator_t
g_conf=ConfigParser.ConfigParser()
               

def task_callback(gearman_worker, job):   
    res_dict={}
    res_dict['header']={}
    res_dict['header']['ip']=g_conf.get("gearman","ip")
    response_dict={}
    global g_adx_interface
    global g_rank_bid   
    global g_filter_obj
    global g_id_obj
    dsp_info_dict={}
    try:
        req_dict=msgpack.unpackb(job.data)
        version=req_dict["header"]["version"]
        adx_req_dict=json.loads(req_dict["request"])
        adx_interface_obj=g_adx_interface.get_obj(version)
        parse_req_dict=adx_interface_obj.parse_bid_request(adx_req_dict)
        region_result_list=g_ip_obj.search(parse_req_dict["ip"])
        parse_req_dict["region"]=region_result_list
        available_idea_list=g_filter_obj.filter(parse_req_dict)
        [win_idea_id,bid]=g_rank_bid.rank_bid(adx_req_dict,available_idea_list,g_idx_mgr["idea"])
        idea_json_dict=g_idx_mgr["idea"].search(win_idea_id)
        bid_info_dict={"bid":bid,"win_idea_id":win_idea_id}
        logging.debug("bid info dict:%s" %(bid_info_dict))
        #create response dict
        response_dict=adx_interface_obj.create_adx_response(parse_req_dict,win_idea_id,idea_json_dict,adx_req_dict,bid)
        dsp_info_dict["bid"]=bid_info_dict
        dsp_info_dict["request"]=parse_req_dict
        #logging.debug("parse req dict:%s" %(parse_req_dict))
    except Exception as e:
        logging.warning("error:%s" %(e))
    logging.info("REQ:\001%s\001%s" %(json.dumps(adx_req_dict),json.dumps(dsp_info_dict)))
    res_dict['response']=response_dict
    logging.debug('response:%s' %(res_dict))
    return msgpack.packb(res_dict)    

class CustomGearmanWorker(gearman.GearmanWorker):    
    def on_job_execute(self, current_job):    
        #print "Job started"   
        return super(CustomGearmanWorker, self).on_job_execute(current_job)    


def server_run(parameter,service_name,task_callback):
    gearman_obj = CustomGearmanWorker(parameter)    
    gearman_obj.register_task(service_name,task_callback)    
    gearman_obj.work()  
   
def init():
    timestamp=datetime.datetime.now().strftime("%Y-%m-%d-%H")
    g_conf.read("../conf/ad_svr.conf")
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../log/ad_svr.'+timestamp+'.log',
                filemode='a')
    service_para=g_conf.get("gearman","para")
    service_name=g_conf.get("gearman","name")
    process_num=int(g_conf.get("gearman","process_num"))
    service_para=service_para.split(',')

    #load adx map
    adx_id_obj=adx_id_map(g_conf)
    global g_adx_interface
    g_adx_interface=adx_interface_t(adx_id_obj,g_conf)
    
    global g_invert_idx_mgr
    g_invert_idx_mgr={}
    ridx_name_list=g_conf.get("index","ridx_list").split(",") 
    for name in ridx_name_list:
        obj=inverted_index_t()
        obj.load_file("../index/"+name+".ridx")
        g_invert_idx_mgr[name]=obj
        #print obj.inverted_dict,name       
    global g_idx_mgr
    g_idx_mgr={}
    idx_name_list=g_conf.get("index","idx_list").split(",") 
    for name in idx_name_list:
        obj=index_t()
        obj.load_file("../index/"+name+".idx")
        g_idx_mgr[name]=obj

    #init ip region
    global g_ip_obj
    g_ip_obj=ip_parse_t(g_conf.get("file","ip_table"),g_conf.get("file","ip_region"))   
    #init id obj
    global g_id_obj
    g_id_obj=transform_id_t(g_conf.get("file","fea_id_file"))
    
    #init fea obj
    extract_fea_obj=extract_feature_t(g_ip_obj,g_id_obj)
    #init model obj
    model_obj=predict_model_t(g_conf.get("file","model"))
    #init idea operator
    operator_obj=idea_operator_t(g_conf.get("file","idea_operate"))

    #init rank bit module
    global g_rank_bid
    g_rank_bid=rank_bid_t(extract_fea_obj,model_obj,operator_obj)
    logging.info("init complete")

    #init filter
    global g_filter_obj
    g_filter_obj=filter_t(g_invert_idx_mgr,g_conf)

    return [service_para,service_name,process_num]

    

if __name__=="__main__":
    [service_para,service_name,process_num]=init()          
    process_list=[]
    for i in range(0,process_num):
        process_obj=multiprocessing.Process(target=server_run, args=(service_para,service_name,task_callback))
        process_list.append(process_obj)
    fp=open(g_conf.get("file","init_done"),"w")
    fp.write("1\n")
    fp.close()
    #start service
    for i in range(0,process_num):
        process_obj=process_list[i]
        process_obj.start()
    for i in range(0,process_num):
        process_obj=process_list[i]
        process_obj.join()
    for i in range(0,process_num):
        process_obj=process_list[i]
        process_obj.quit()
