#!/usr/bin/env
# -*- coding: utf-8 -*-
import ConfigParser
import logging
import sys
import json
from ip_region_parse import ip_parse_t

g_conf=ConfigParser.ConfigParser()

    


def extract_feature(fea_dict):
    global g_ip_obj 
    ip_str=fea_dict["device"]["ip"]
    region_result_list=g_ip_obj.search(ip_str)
    if region_result_list!=None:
        first_id=region_result_list[2]
        second_id=region_result_list[3]
        first_region_name=str(region_result_list[-2])
        second_region_name=str(region_result_list[-1])
        region_feature_list=[str(first_id),str(second_id),first_region_name,second_region_name]
        region_feature="region"+"-"+"-".join(region_feature_list)
        return region_feature
    else:
        logging.warning("ip not found[%s]" %(ip_str))
   
    
def process(input_file,output_file):
    input_fp=open(input_file,"r")    
    output_fp=open(output_file,"w")
    global g_ip_obj
    g_ip_obj=ip_parse_t("../data/ip.all","../data/region.txt")
    line_cnt=0
    for line in input_fp:
        line_cnt+=1
        line=line.rstrip("\r\n").split("\t")
        req_json=line[4]
        click=int(line[2])
        try:
            req_dict=json.loads(req_json)
            fea_json_dict=json.loads(req_dict["request"])
        except:
            logging.warning("load json failed[%d]" %(line_cnt))
            continue
        region_feature=extract_feature(fea_json_dict)                         
        output_fp.write("%s\t%s\t%s\n" %(line[2],line[3],region_feature))
   
def init():
    g_conf.read("../conf/extract_feature.conf")
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../log/extract_feature.log',
                filemode='a')
    

if __name__=="__main__":
    input_file=sys.argv[1]
    output_file=sys.argv[2]
    init()
    process(input_file,output_file)
