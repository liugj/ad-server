#!/usr/bin/env
# -*- coding: utf-8 -*-

import ConfigParser
import logging
import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')
g_conf=ConfigParser.ConfigParser()

def process(fea_set_file,result_file):
    fea_set_fp=open(fea_set_file,"r")
    result_fp=open(result_file,"w")
    analysis_dict={}
    fea_name_list=[]
    line_cnt=0
    for line in fea_set_fp:
        line=line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            for i in range(2,len(line)):
                fea_name=line[i]
                sub_dict={}
                analysis_dict[fea_name]=sub_dict
                fea_name_list.append(fea_name)
            continue
        click=int(line[0])
        for i in range(2,len(line)):
            fea_value_list=line[i].split("\001")
            fea_name=fea_name_list[i-2]
            sub_dict=analysis_dict[fea_name]
            for fea_value in fea_value_list:
                if fea_value in sub_dict:
                    [old_show,old_click]=sub_dict[fea_value]
                    old_show+=1
                    old_click+=click
                    sub_dict[fea_value]=[old_show,old_click]
                else:
                    sub_dict[fea_value]=[1,click]
            analysis_dict[fea_name]=sub_dict
    for fea_name in analysis_dict:
        sub_dict=analysis_dict[fea_name]
        for fea_value in sub_dict:
            [show,click]=sub_dict[fea_value]
            sub_dict[fea_value]=[show,click,float(click)/show]
        analysis_dict[fea_name]=sub_dict
        
    for fea_name in analysis_dict:
        sub_dict=analysis_dict[fea_name]
        for fea_value,data_list in sorted(sub_dict.items(),lambda x,y:cmp(x[1][2],y[1][2]),reverse=True):
            result_fp.write("%s\t%s\t%d\t%d\t%f\n" %(fea_name,fea_value,data_list[0],data_list[1],data_list[2]))
    result_fp.close()
    fea_set_fp.close()
          
def init():
    g_conf.read("../conf/analysis.conf")
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../log/analysis.log',
                filemode='a')
    

if __name__=="__main__":
    init()
    fea_set_file=sys.argv[1]
    result_file=sys.argv[2]
    process(fea_set_file,result_file)


