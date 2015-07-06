#!/usr/bin/env
# -*- coding: utf-8 -*-
import json
import sys
from ip_region_parse import ip_parse_t
import logging
def tongji(req_file):
    ip_obj=ip_parse_t("../data/ip.all","../data/region.txt")
    output_fp=open("../data/region_result","w")
    line_cnt=0
    fp=open(req_file,"r")
    for line in fp:
        line_cnt+=1
        line=line.rstrip("\r\n").split("\001")
        try:
            json_dict=json.loads(line[1])
            request_dict=json.loads(json_dict["request"])
            ip_str=request_dict["device"]["ip"]
            region_result_list=ip_obj.search(ip_str)
            if region_result_list!=None:
                output_fp.write("%s\t%d\t%d\n" %(ip_str,region_result_list[2],region_result_list[3]))
            else:
                logging.warning("ip not found[%s]" %(ip_str))
                continue
        except:
            logging.warning("extract content failed[%d]" %(line_cnt))
            continue
    fp.close()


if __name__=="__main__":
    req_file=sys.argv[1]
    tongji(req_file)
