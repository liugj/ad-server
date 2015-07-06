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
g_conf=ConfigParser.ConfigParser()

               

def task_callback(gearman_worker, job):   
    res_dict={}
    res_dict['header']={}
    res_dict['header']['ip']=g_conf.get("gearman","ip")
    bid_dict={}
    try:
        req_dict=msgpack.unpackb(job.data)
        #req_bid_dict=json.loads(req_dict['request'])
        #imp_dict=req_bid_dict['imp'][0]
        #bid_dict['imp_id']=imp_dict['impid']
        #bid_result_dict=g_bid_process.bid_decide(req_bid_dict)       
        #if bid_result_dict==None:
        #    bid_dict['result']={}
        #else:
        #    bid_dict['result']=bid_result_dict
    except Exception as e:
        logging.warning("error:%s" %(e))
    logging.info("req:\001%s" %(json.dumps(req_dict)))
    logging.info("req imp:%s" %(json.loads(req_dict["request"])))
    res_dict['response']=bid_dict
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
    g_adx_interface=adx_interface_t(adx_id_obj)
    logging.info("init complete")
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
    #for i in range(0,process_num):
    #    process_obj=process_list[i]
    #    process_obj.quit()
