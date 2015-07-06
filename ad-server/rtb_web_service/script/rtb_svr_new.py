#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
import nginx_uwsgi
import logging
import ConfigParser
import urllib
import types
import json
import sys
#from ad_svr_client import Client
#import msg_pb2
import time
from gearman import GearmanClient
import msgpack
from message import *
import datetime
web.config.debug = False 
#g_client=Client()
class parameter_t:
    def __init__(self):
        self.timeout=0.1
        self.ip=None     
        self.svr_name=None   

class mongo_rtb: 
    def POST(self): 
        global g_gearman_client
        global g_para
        global g_conf
        req_urlcode=web.data()
        req_json=urllib.unquote(req_urlcode) 
        start_time=time.time()  
        try:
            req_dict={}
            req_dict['header']={}
            req_dict['header']['ip']=g_para.ip
            req_dict['request']=req_json 
            req_dict['header']['channel']="mongo"
            req_dict['header']['version']=g_conf.get("mongo","version")  
            logging.info("%s" %(req_dict))
            ret_result=g_gearman_client.submit_job(g_para.svr_name,msgpack.packb(req_dict),poll_timeout=g_para.timeout)
        except Exception as e:
            logging.warning("error:%s" %(e))            
            ret_result=None
        bid_dict=msgpack.unpackb(ret_result.result)
        response_dict=get_message(json.loads(req_json),bid_dict)
        end_time=time.time()
        logging.info("time cost:%f" %(end_time-start_time))
        logging.debug("return adx:\t%s" %(json.dumps(response_dict)))
        return response_dict
          
class mongo_win_notice: 
    def GET(self): 
        win_dict={}
        for key,value in web.input().items():
            win_dict[key]=value
        logging.info("win_notice:\t%s" %(json.dumps(win_dict)))
        return "success"

def init():
    #init log
    global g_gearman_client
    global g_para
    global g_conf
    g_conf=ConfigParser.ConfigParser()
    timestamp=datetime.datetime.now().strftime("%Y-%m-%d")
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S ',
                filename='../log/rtb_new.log.'+timestamp,
                filemode='a')
    #init conf
    g_conf.read("../conf/rtb_new.conf")
 
    #init gearman client
    gearman_list=g_conf.get("gearman","client").split(',')   
    g_gearman_client=GearmanClient(gearman_list)
    g_para=parameter_t()
    g_para.ip=g_conf.get("gearman","ip")
    g_para.timeout=float(g_conf.get("gearman","timeout"))
    g_para.svr_name=g_conf.get("gearman","svr_name")

    return 0


if __name__ == "__main__": 
    ret=init()
    if ret<0:
        logging.warning("init failed")
        sys.exit(-1)
    urls = ('/mongo_rtb', 'mongo_rtb',
            '/mongo_win_notice','mongo_win_notice'
    ) 
    app = web.application(urls, globals()) 
    app.run() 

