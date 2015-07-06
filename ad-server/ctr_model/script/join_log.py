#!/usr/bin/env
# -*- coding: utf-8 -*-
import ConfigParser
import logging
import sys
import json

g_conf=ConfigParser.ConfigParser()

def join_log(show_log,click_log,req_log,charge_log,join_log_file):
    session_info_dict={}
    #read show log
    fp=open(show_log,"r")
    session_dict={}
    for line in fp:
        line=line.rstrip("\r\n").split(" ")
        #if line[-1]=="idea_id=14":
        #    continue
        list=line[-2].split("=")
        session_id=list[1]
        date=line[0]
        time=line[1]
        session_info_dict[session_id]=[date,time,0,0]
    fp.close()
    #read click log 
    fp=open(click_log,"r")
    for line in fp:
        line=line.rstrip("\r\n").split(" ")
        list=line[-2].split("=")
        session_id=list[1]
        date=line[0]
        time=line[1]
        if not(session_id in session_info_dict):
            logging.warning("no such session id[%s] in show log" %(session_id))
            continue
        session_info_dict[session_id]=[date,time,1,0]
    fp.close()

    #read charge log
    fp=open(charge_log,"r")
    cnt=0
    for ori_line in fp:
        line=ori_line.rstrip("\r\n").split("\t")
        cnt+=1
        if len(line)!=3:
            logging.warning("invalid charge log line cnt[%d]" %(cnt))
            continue
        list=line[2].split(" ")
        if len(list)<7:
            logging.warning("invalid charge log cnt[%d]" %(cnt))
            continue
        session_info=(list[6].split("="))
        if len(session_info)!=2:
            logging.warning("invalid session info in charge log cnt[%d]" %(cnt))
            continue
        session_id=session_info[1]
        if not(session_id in session_info_dict):
            logging.warning("no such charge session id[%s] in session info dict" %(session_id))
            continue
        charge=int(line[0])
        #print session_info_dict[session_id]
        session_info_dict[session_id][3]=charge
    fp.close()
    click_num=0
    charge_sum=0
    for key in session_info_dict:
        click_num+=session_info_dict[key][2]
        charge_sum+=session_info_dict[key][3]
    charge_sum=float(charge_sum)/100000
    logging.info("show:%d click:%d ctr:%f charge_sum:%f click_cost:%f" %(len(session_info_dict),click_num,float(click_num)/len(session_info_dict),charge_sum,charge_sum/click_num))    
    
    output_fp=open(join_log_file,"w")
    #join req log
    fp=open(req_log,"r")
    line_cnt=0
    for line in fp:
        line_cnt+=1
        line=line.rstrip("\r\n").split("\001")
        try:
            json_dict=json.loads(line[1])
            request_dict=json.loads(json_dict["request"])
            imp_dict=request_dict["imp"]
            imp_id=imp_dict[0]["impid"].encode('utf8')
            if imp_id in session_info_dict:
                [date,time,click,charge]=session_info_dict[imp_id]               
                output_fp.write("%s\t%s\t%d\t%d\t%s\n" %(date,time,click,charge,line[1]))
            #else:
            #    output_fp.write("%s\t%s\t%d\t%d\t%s\n" %(date,time,click,0,line[1]))
        except:
            logging.warning("extract content failed[%d]" %(line_cnt))
            continue
    fp.close()
    output_fp.close()




def init():
    g_conf.read("../conf/join_log.conf")
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../log/join_log.log',
                filemode='a')
    



if __name__=="__main__":
    show_log=sys.argv[1]
    click_log=sys.argv[2]
    req_log=sys.argv[3]
    charge_log=sys.argv[4]
    join_log_file=sys.argv[5]
    init()
    join_log(show_log,click_log,req_log,charge_log,join_log_file)

