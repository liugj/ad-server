#!/usr/bin/env
# -*- coding: utf-8 -*-
import ConfigParser
import logging
import sys
import json
import glob
import re
reload(sys)
sys.setdefaultencoding('utf-8')
g_conf=ConfigParser.ConfigParser()
from ctypes import *
import ctypes
g_calc_price=ctypes.CDLL("./libdecrypter.so")

def process(charge_log_path,nginx_log_path,ad_svr_log_path,date_str,join_log_path):
    [year,month,day]=date_str.split("-")
    charge_file_prefix=charge_log_path+"/charge_python."+year+month+day+"*"
    charge_file_list=glob.glob(charge_file_prefix)
    cost_dict={}
    '''
    #parse charge log
    for charge_file in charge_file_list:
        fp=open(charge_file,"r")
        for line in fp:
            line=line.rstrip("\r\n")
            pattern=re.compile(".*WIN_NOTICE\:(.*)")
            result_list=pattern.match(line)
            if result_list!=None:
                json_str=result_list.group(1)
                json_dict=json.loads(json_str)
                impid=json_dict["impid"]
                cost=json_dict["cost"]
                cost_dict[impid]=cost
        fp.close()    
    '''
    #parse nginx log
    ad_action_dict={}
    nginx_file_prefix=nginx_log_path+"/"+year+month+day+"*"
    nginx_file_list=glob.glob(nginx_file_prefix)
    for nginx_file in nginx_file_list:
        fp=open(nginx_file,"r")
        pattern=re.compile(r'^(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\s-\s(.*)\s\[(.*)\]\s\"(.*)\"\s(\d{3,})\s(\d+)\s\"([^\s]*)\"\s\"(.*?)\"\s\"(.*)\"$')
        for line in fp:
            line=line.rstrip("\r\n")
            try:
                pattern2=re.compile(r"GET /track.gif\?(.*?)HTTP")
                result=pattern.match(line)
                ip=result.group(1)
                url_ori=result.group(4)
                item_str=pattern2.match(url_ori).group(1)       
            except:
                logging.warning("invalid line:%s" %(line))
                continue   
            item_list=item_str.split("$$$")
            dict_temp={}
            for item_info in item_list:
                item_info_list=item_info.split("*")
                key=item_info_list[0]
                value=item_info_list[1]
                dict_temp[key]=value
            impid=dict_temp["id"]
            action_type=dict_temp["type"]
            if not(impid in ad_action_dict):
                sub_dict={"show":0,"click":0,"download":0,"install":0,"open":0,"cost":0}
            else:
                sub_dict=ad_action_dict[impid]
            sub_dict[action_type]=1
            if "win_price" in dict_temp:
                cost=g_calc_price.TestWinningPrice(dict_temp["win_price"])
                sub_dict["cost"]=cost
            ad_action_dict[impid]=sub_dict
        fp.close()    
    #join ad log path
    ad_svr_prefix=ad_svr_log_path+"/ad_svr."+year+"-"+month+"-"+day+"*"
    ad_svr_log_list=glob.glob(ad_svr_prefix)
    output_fp=open(join_log_path+"/join_log."+date_str,"w")
    for ad_svr_file in ad_svr_log_list:
        fp=open(ad_svr_file,"r")
        for line in fp:
            line=line.rstrip("\r\n").split("\001")
            if len(line)!=3:
                continue
            time_str=line[0].split(" ")[1].rstrip("]")
            json_dict=json.loads(line[1])
            impid=json_dict["imp"][0]["impid"]
            if not(impid in ad_action_dict):
                continue
            ad_action_sub_dict=ad_action_dict[impid]
            output_fp.write("%s\t%s\t%s\t%s\n" %(time_str,json.dumps(ad_action_sub_dict),line[1],line[2]))
        fp.close()
    

def init():
    g_conf.read("../conf/merge_log.conf")
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../log/merge_log.log',
                filemode='a')

if __name__=="__main__":
    init()
    charge_log_path=sys.argv[1]
    nginx_log_path=sys.argv[2]
    ad_svr_log_path=sys.argv[3]     
    date_str=sys.argv[4]
    join_log_path=sys.argv[5]
    process(charge_log_path,nginx_log_path,ad_svr_log_path,date_str,join_log_path)
    
