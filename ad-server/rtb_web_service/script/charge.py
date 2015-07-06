#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import ConfigParser
from mysql_db import *
import sys
import time
def charge_process(charge_file):
    fp=open(charge_file,"r")
    date=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    #date=date_tmp
    #cur_hour=int(time.strftime('%H',time.localtime(time.time())))
    cost_dict={}
    for line in fp:
        line=line.rstrip("\r\n").split("\t")
        cost=int(line[0])
        detail_list=line[-1].split(' ')
        hour=int((detail_list[1].split(':'))[0])
        idea_list=detail_list[-1].split('=')
        idea_id=idea_list[1]
        if cost==0 or not(idea_id in g_ad_dict):
            continue
        cost=float(cost)/100000
        if idea_id in cost_dict:
            cost_dict[idea_id]+=cost
        else:
            cost_dict[idea_id]=cost
    for idea_id in cost_dict:
        cost=cost_dict[idea_id]
        [unit_id,account_id]=g_ad_dict[idea_id]
       
        if unit_id in g_ad_profit_dict:
            profit=g_ad_profit_dict[unit_id]
        else:
            profit=float(g_conf.get("data","default_profit"))
        
        #update total cost
        sql="select cost from cost where date='%s'" %(date)
        logging.info("get cost sql:%s" %(sql))
        [result_num,result_array]=g_mysql.sql_query(sql,"consume")    
        total_cost=result_array[0][0]
        total_cost+=cost
        sql="update cost set cost='%d' where date='%s'" %(total_cost,date)
        logging.info("update cost sql:%s" %(sql))
        [result_num,result_array]=g_mysql.sql_query(sql,"consume")    
        #update account cost
        get_sql="select cost from account_cost where id='%s' and date='%s' and hour='%d'" %(unit_id,date,hour)
        logging.info("get account_cost sql:%s" %(get_sql))
        [result_num,result_array]=g_mysql.sql_query(get_sql,"consume")    
        user_cost=cost*(1+profit)
        logging.info("cost:%d user cost:%d profit:%f unit_id:%s idea_id:%s" %(cost,user_cost,profit,unit_id,idea_id))

        if result_num==0:
            sql="insert into account_cost values('%s','%d','%d','%s','%d')" %(unit_id,0,user_cost,date,hour)   
            logging.info("insert account_cost sql:%s" %(sql))
            [result_num,result_array]=g_mysql.sql_query(sql,"consume")    
        else:
            [result_num,result_array]=g_mysql.sql_query(get_sql,"consume")    
            total_cost=result_array[0][0]
            total_cost+=user_cost
            sql="update account_cost set cost='%d' where id='%s' and date='%s' and hour='%d'" %(total_cost,unit_id,date,hour)   
            
            [result_num,result_array]=g_mysql.sql_query(sql,"consume")    
        #update account balance
        get_sql="select account_balance from account where id='%s'"  %(account_id) 
        [result_num,result_array]=g_mysql.sql_query(get_sql,"ad_new")    
        account_balance=result_array[0][0]
        account_balance=account_balance-user_cost          
        update_sql="update account set account_balance='%d' where id='%s'" %(account_balance,account_id)
        g_mysql.update_query(update_sql,"ad_new")    
        logging.info("sql:%s account_id:%s account_balance:%d" %(update_sql,account_id,account_balance))
    fp.close()   

       
def init():
    #init log
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S ',
                filename='../log/charge_python.log',
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
    global g_ad_dict
    g_ad_dict={}
    ad_file=g_conf.get('file','ad_file')
    fp=open(ad_file,"r")
    line_cnt=0
    for line in fp:
        line_cnt+=1
        line=line.rstrip("\r\n").split("\t")
        if line_cnt==1:
            continue
        idea_id=line[0]
        unit_id=line[1]
        account_id=line[3]
        g_ad_dict[idea_id]=[unit_id,account_id]
    fp.close()
     
    global g_ad_profit_dict 
    g_ad_profit_dict={}   
    ad_profit_file=g_conf.get('file','ad_profit')
    fp=open(ad_profit_file,"r")
    line_cnt=0
    for line in fp:
        line_cnt+=1
        line=line.rstrip("\r\n").split("\t")
        if line_cnt==1:
            continue
        unit_id=line[0]
        profit=float(line[2])
        g_ad_profit_dict[unit_id]=profit
    fp.close()
    
    return 0


if __name__ == "__main__": 
    ret=init()
    if ret<0:
        logging.warning("init failed")
        sys.exit(-1)
    charge_file=sys.argv[1]
    charge_process(charge_file)
    g_mysql.close_connection()
    
