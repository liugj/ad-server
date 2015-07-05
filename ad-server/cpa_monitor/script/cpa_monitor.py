#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
import nginx_uwsgi
import logging
#from mysql_db import *
import ConfigParser
import sys
import json
import datetime

class test: 
    def GET(self,msg):
        try:
            remote_ip=web.ctx.env.get('REMOTE_ADDR')
        except:
            logging.warning("get remote ip failed")
            remote_ip=""
        input_dict={}
        for key,value in web.input().items():
            input_dict[key]=value
        input_dict["remote_ip"]=remote_ip
        logging.info("open app\t%s" %(json.dumps(input_dict)))

def init():
    #init log
    timestamp=datetime.datetime.now().strftime("%Y-%m-%d")
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S ',
                filename='../log/cpa.'+timestamp+'.log',
                filemode='a')
    logging.info("init completed")
    #init db 
    return 0


if __name__ == "__main__": 
    ret=init()
    if ret<0:
        logging.warning("init failed")
        sys.exit(-1)

    urls = ('/(.*)','test') 
    app = web.application(urls, globals()) 
    app.run() 

