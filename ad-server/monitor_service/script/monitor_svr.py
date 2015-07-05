#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
import nginx_uwsgi
import logging
import ConfigParser
#from mysql_db import *
import sys
import json
import datetime

class click: 
    def GET(self): 
        click_dict={}
        for key,value in  web.input().items():
            click_dict[key]=value
        logging.info("ad_click detail:\t%s" %(json.dumps(click_dict)))
        if not "click_type" in click_dict:
            logging.warning("no click type")
            return None
        click_type=click_dict["click_type"]
        if click_type=="webpage":
            if not "click_addr" in click_dict:
                logging.warning("no click addr")
                return None
            click_addr=click_dict["click_addr"]   
            web.seeother(click_addr)
        
class show: 
    def GET(self): 
        show_dict={}
        for key,value in  web.input().items():
            show_dict[key]=value
        logging.info("ad_show detail:\t%s" %(json.dumps(show_dict)))
        return None

       
def init():
    #init log
    timestamp=datetime.datetime.now().strftime("%Y-%m-%d")
    
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S ',
                filename='../log/monitor.'+timestamp+".log",
                filemode='a')
    #init conf
    global g_conf
    global g_mysql
    global g_idea_dict
    g_idea_dict={}
    g_conf=ConfigParser.ConfigParser()
    g_conf.read("../conf/monitor.conf")
    return 0


if __name__ == "__main__": 
    ret=init()
    if ret<0:
        logging.warning("init failed")
        sys.exit(-1)

    urls = ('/show', 'show',
            '/click','click'
    ) 
    app = web.application(urls, globals()) 
    app.run() 
    g_mysql.close_connection()   

