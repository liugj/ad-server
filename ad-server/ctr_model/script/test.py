#!/usr/bin/env
# -*- coding: utf-8 -*-
import json
import sys
from ip_region_parse import ip_parse_t
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
app_type_dict={}
fp=open("../data/apptype.txt","r")
for line in fp:
    line=line.rstrip("\r\n").split("\t")
    id=line[2]
    name=line[1]
    app_type_dict[id]=name

fp=open(sys.argv[1],"r")
tongji_dict={}
for line in fp:
    line=line.rstrip("\r\n").split("\t")
    req_json=line[4]
    click=int(line[2])
    try:
        req_dict=json.loads(req_json)
        fea_json_dict=json.loads(req_dict["request"])
    except:
        logging.warning("load json failed[%d]" %(line_cnt))
        continue
    app_name=fea_json_dict["app"]["name"]
    cat_list=[]
    for i in range(0,len(fea_json_dict["app"]["cat"])):
        cat_id=fea_json_dict["app"]["cat"][i]
        cat_name=app_type_dict[cat_id]
        cat_list.append(cat_name)
    cat_type=",".join(cat_list)
    if app_name in tongji_dict:
        [count,cat_type,click_sum]=tongji_dict[app_name]
        tongji_dict[app_name]=[count+1,cat_type,click_sum+click]
    else:
        tongji_dict[app_name]=[1,cat_type,click]

for key,value in sorted(tongji_dict.items(),lambda x,y:cmp(x[1],y[1]),reverse=True):
    print key,value[0],value[1],value[2],float(value[2])/value[0]
