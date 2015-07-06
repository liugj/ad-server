#!/usr/bin/env
# -*- coding: utf-8 -*-

import logging
from mysql_db import *

def init():
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S ',
                filename='../log/get_mysql_data.log',
                filemode='a')
    #init conf
    global g_conf
    global g_mysql
    g_conf=ConfigParser.ConfigParser()
    g_conf.read("../conf/charge_python.conf")
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
    

if __name__=="__main__":
    

