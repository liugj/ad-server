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
cat_dict={}
line_cnt=0
for line in fp:
    line=line.rstrip("\r\n").split("\001")
    req_json=line[1]
    line_cnt+=1
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
    for cat_name in cat_list:
        if cat_name in tongji_dict:
            sub_dict=tongji_dict[cat_name]    
            cat_dict[cat_name]+=1
        else:
            cat_dict[cat_name]=1
            sub_dict={}
        if app_name in sub_dict:
            sub_dict[app_name]+=1
        else:
            sub_dict[app_name]=1
        tongji_dict[cat_name]=sub_dict
        break      

output_fp=open("../tmp/app_sort","w")
for cat_name,count in sorted(cat_dict.items(),lambda x,y:cmp(x[1],y[1]),reverse=True):
    output_fp.write("cat\t%s\t%d\n" %(cat_name,count))
    if cat_name in tongji_dict:
        sub_dict=tongji_dict[cat_name]
        for app_name,app_count in sorted(sub_dict.items(),lambda x,y:cmp(x[1],y[1]),reverse=True):
            output_fp.write("app\t%s\t%d\t%s\n" %(app_name,app_count,cat_name))

output_fp.close()
