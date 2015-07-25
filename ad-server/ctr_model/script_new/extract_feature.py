#!/usr/bin/env
# -*- coding: utf-8 -*-
import ConfigParser
import logging
import sys
import json
from ip_region_parse import ip_parse_t
from transform_id import transform_id_t
reload(sys)
sys.setdefaultencoding('utf-8')
g_conf=ConfigParser.ConfigParser()



class extract_feature_t():
    def __init__(self):
        pass

    def extract(self,value,feature_name):
        if feature_name=="region":
            return self.extract_region(value)
        else:
            return self.direct_show(value,feature_name)
    
    def direct_show(self,value,feature_name):
        return feature_name+"-"+value   
    
    def extract_region(self,ip_str):
        global g_ip_obj 
        region_result_list=g_ip_obj.search(ip_str)
        if region_result_list!=None:
            first_id=region_result_list[2]
            second_id=region_result_list[3]
            first_region_name=str(region_result_list[-2])
            second_region_name=str(region_result_list[-1])
            region_feature_list=[str(first_id),str(second_id),first_region_name,second_region_name]
            region_feature="region-"+str(first_id)+"-"+first_region_name
            if second_region_name!=None:
                region_feature+="\001"+"region-"+str(second_id)+"-"+second_region_name
            return region_feature
        else:
            logging.warning("ip not found[%s]" %(ip_str))
            return "region-0"
   



def extract_feature(time_str,fea_dict,single_fea_list,combine_fea_list):
    global g_id_obj
    ip_str=fea_dict["device"]["ip"]
    time_list=time_str.split(":")
    hour=time_list[0]
    app_name=fea_dict["app"]["name"]
    app_type=fea_dict["app"]["cat"][0]
    app_id=fea_dict["app"]["aid"]
    manufacture=fea_dict["device"]["make"].lower()
    device_id=fea_dict["device"]["dpid"]
    ori_data_list=[ip_str,app_id+"-"+app_name,hour,app_type,manufacture]
    fea_obj=extract_feature_t()
    result_fea_dict={}
    for i in range(0,len(single_fea_list)):
        fea_name=single_fea_list[i]      
        ori_value=ori_data_list[i]
        fea_str=fea_obj.extract(ori_value,fea_name)
        result_fea_dict[fea_name]=fea_str
    for combine_fea_name in combine_fea_list:
        list_temp=combine_fea_name.split("-")
        fea_name1=list_temp[1]
        fea_name2=list_temp[2]
        fea_list1=result_fea_dict[fea_name1].split("\001")
        fea_list2=result_fea_dict[fea_name2].split("\001")
        combine_fea_value=""
        for fea_value1 in fea_list1:
            for fea_value2 in fea_list2:
                combine_fea_value+=fea_value1+"-"+fea_value2
                combine_fea_value+="\001"
        combine_fea_value=combine_fea_value.rstrip("\001")
        result_fea_dict[combine_fea_name]=combine_fea_value
    fea_str=""
    for feature in single_fea_list:
        fea_str+=result_fea_dict[feature]+"\t"
    for feature in combine_fea_list:
        fea_str+=result_fea_dict[feature]+"\t"
    fea_str=fea_str.rstrip("\t")
    fea_id_list=[]
    fea_id_str=""
    list_temp=fea_str.split("\t")
    for fea_name in list_temp:
        fea_id=g_id_obj.get_id(fea_name)
        fea_id_list.append(fea_id)
    fea_id_list.sort()
    for fea_id in fea_id_list:
        fea_id_str+=str(fea_id)+":1"+" "
    fea_id_str=fea_id_str.rstrip(" ")
    return (fea_str,fea_id_str)

def process(input_file,fea_output_file,ml_file,type):
    input_fp=open(input_file,"r")    
    fea_fp=open(fea_output_file,"w")
    ml_fp=open(ml_file,"w")
    global g_ip_obj
    global g_id_obj
    g_ip_obj=ip_parse_t("../data/ip.all","../data/region.txt")
    g_id_obj=transform_id_t(g_conf.get("file","fea_id_file"))
    line_cnt=0
    single_feature_list=["region","app","time","app_type","manufacture"]
    #combine_feature_list=["combine-region-time","combine-app-region"]
    #combine_feature_list=["combine-region-time"]
    combine_feature_list=[]
    header="click\tdownload\tinstall\topen\tconsume\t"+"\t".join(single_feature_list)+"\t"+"\t".join(combine_feature_list)+"\n"
    fea_fp.write(header)
    for line in input_fp:
        line_cnt+=1
        line=line.rstrip("\r\n").split("\t")
        time_str=line[0]
        try:
            fea_json_dict=json.loads(line[2])
        except:
            logging.warning("load json failed[%d]" %(line_cnt))
            continue
        (fea_str,fea_id_str)=extract_feature(time_str,fea_json_dict,single_feature_list,combine_feature_list)                         
        ad_action_dict=json.loads(line[1])
        click=ad_action_dict["click"]
        download=ad_action_dict["download"]
        install=ad_action_dict["install"]
        app_open=ad_action_dict["open"]
        consume=ad_action_dict["cost"]
        fea_fp.write("%d\t%d\t%d\t%d\t%d\t%s\n" %(click,download,install,app_open,consume,fea_str))
        #transform to id
        if type=="train" and download==1:
            count=5
        else:
            count=1
        for i in range(0,count):
            ml_fp.write("%d %s\n" %(click,fea_id_str))

def init():
    g_conf.read("../conf/extract_feature.conf")
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../log/extract_feature.log',
                filemode='a')
    

if __name__=="__main__":
    input_file=sys.argv[1]
    fea_output_file=sys.argv[2]
    ml_file=sys.argv[3]
    type=sys.argv[4]
    init()
    process(input_file,fea_output_file,ml_file,type)
    g_id_obj.update_fea_file()
