#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
import nginx_uwsgi
import logging
import ConfigParser
import urllib
import types
import json
from request_bid import *

web.config.debug = False 
g_conf=ConfigParser.ConfigParser()

class rtb: 
    def POST(self): 
        req_urlcode=web.data()
        req_json=urllib.unquote(req_urlcode)   
        logging.info("req:%s" %(req_json))
        try:
            req_dict=json.loads(req_json)
        except:
            logging.warning("parse request failed")
            return None
        response_dict=bid_response(req_dict)        
        logging.info("response:	%s" %(response_dict))
        return response_dict
          
class win_notice: 
    def GET(self): 
        dict=web.input()
        if not("id" in dict):
            logging.warning("no id in win notice url")
            return None
        win_info=dict["id"]
        win_info_list=dict["id"].split("=")
        if len(win_info_list)!=2:
            logging.warning("invalid win str[%s]" %(win_info))
            return None
        logging.info("win_notice id=%s price=%s" %(win_info_list[0],win_info_list[1]))
        return "success"

def init():
    #init log
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S ',
                filename='../log/rtb.log',
                filemode='a')
    #init conf
    g_conf.read("../conf/rtb.conf")

    #init db 
    return 0


if __name__ == "__main__": 
    ret=init()
    if ret<0:
        logging.warning("init failed")
        sys.exit(-1)

    urls = ('/bid', 'rtb',
            '/win_notice','win_notice'
    ) 
    app = web.application(urls, globals()) 
    app.run() 

