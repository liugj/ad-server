#!/usr/bin/python
# -*- coding: utf-8 -*-

import web
import nginx_uwsgi
import logging
import ConfigParser
from mysql_db import *
import sys


class click: 
    def GET(self): 
        global g_mysql
        dict=web.input()
        if not("id" in dict):
            logging.warning("no id in click url")
            return None
        if not("idea_id" in dict):
            logging.warning("no idea_id in click url")
            return None
        session_id=dict["id"]
        idea_id=dict["idea_id"]
        logging.info("ad_click id=%s idea_id=%s" %(session_id,idea_id))
        #try:
            #sql="select landingpage from idea where id='%s'" %(idea_id)
            #[result_num,result_array]=g_mysql.sql_query(sql,"ad_new")
            #logging.debug("sql:%s" %(sql))
            #landingpage="http://lp.shoozen.net/index.php/welcome/download/"+session_id
        if not(idea_id in g_idea_dict):
            logging.warning("no such idea id[%s]" %(idea_id))
            return None
        landingpage=g_idea_dict[idea_id]
        logging.info("click session id:%s landingpage:%s" %(session_id,landingpage))
        #except Exception , e:
        #    logging.info("error :%s" %(e))
        web.seeother(landingpage)
        #return None

class show: 
    def GET(self): 
        dict=web.input()
        if not("id" in dict):
            logging.warning("no id in show url")
            return None
        if not("idea_id" in dict):
            logging.warning("no idea_id in click url")
            return None
        session_id=dict["id"]
        idea_id=dict["idea_id"]
        logging.info("ad_show id=%s idea_id=%s" %(session_id,idea_id))
        return None

       
def init():
    #init log
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S ',
                filename='../log/monitor.log',
                filemode='a')
    #init conf
    global g_conf
    global g_mysql
    global g_idea_dict
    g_idea_dict={}
    g_conf=ConfigParser.ConfigParser()
    g_conf.read("../conf/monitor.conf")
    g_mysql=mysql_db()
    db_name=g_conf.get("db","db_name")
    host=g_conf.get("db","host")
    user_name=g_conf.get("db","user_name")
    passwd=g_conf.get("db","passwd")
    port_num=int(g_conf.get("db","port_num"))
    ret=g_mysql.establish_connection(host,user_name,passwd,port_num)
    if ret!=0:
        logging.warning("connect to db failed")
        return -1
    #init db 
        
    #init idea dict
    idea_file=g_conf.get("file","idea_file")
    line_cnt=0
    header_dict={}
    fp=open(idea_file,"r")
    print idea_file
    for line in fp:
        line_cnt+=1
        line=line.rstrip("\r\n").split("\t")
        if line_cnt==1:
            for i in range(0,len(line)):
                name=line[i]
                header_dict[name]=i
            continue    
        idea_id=line[0] 
        lp_idx=header_dict['landingpage']
        lp=line[lp_idx]       
        g_idea_dict[idea_id]=lp
    fp.close()
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

