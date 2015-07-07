#!/usr/bin/env
# -*- coding: utf-8 -*-
import logging
import time

class ip_parse_t:
    def transform_ip(self,ip_str):
        ip_long=0
        figure_list=ip_str.split(".")
        pos=3
        factor=1
        result=0
        combine_str=""
        while pos>=0:
            result+=int(figure_list[pos])*factor
            factor=factor*256
            pos=pos-1    
        return result


    def __init__(self,ip_file,region_file):
        self.region_dict={}
        self.ip_list=[]
        
        #load region file
        fp=open(region_file,"r")
        line_cnt=0
        for line in fp:
            line_cnt+=1
            if line_cnt==1:
                continue
            line=line.rstrip("\r\n").split("\t")
            area_name=line[2]
            if line[1]=="0":
                region_id=int(line[0])
                parent_id=int(line[1])
            else:
                region_id=int(line[1])
                parent_id=int(line[0])
            self.region_dict[region_id]=[parent_id,area_name]
        fp.close()
        #load  ip region table      
        fp=open(ip_file,"r")
        dict_temp={}
        for line in fp:
            line=line.rstrip("\r\n").split("\t")
            start_ip=self.transform_ip(line[0])
            end_ip=self.transform_ip(line[1])
            first_region_id=int(line[2])
            second_region_id=int(line[3])
            if first_region_id!=0 and first_region_id in self.region_dict:
                first_region_name=self.region_dict[first_region_id][1]
            else:
                first_region_name=None
            if second_region_id!=0 and second_region_id in self.region_dict:
                second_region_name=self.region_dict[second_region_id][1]
            else:
                second_region_name=None
                dict_temp[second_region_id]=1
            self.ip_list.append([start_ip,end_ip,first_region_id,second_region_id,line[0],line[1],first_region_name,second_region_name])
        fp.close()
        #print dict_temp

    def search(self,ip_str):
        ip_long=self.transform_ip(ip_str)
        begin=0        
        end=len(self.ip_list)-1
        pos=(begin+end)/2 
        while begin<=end:
            current_list=self.ip_list[pos]
            if ip_long>=current_list[0] and ip_long<=current_list[1]:
                return current_list
            elif ip_long>current_list[0]:
                begin=pos+1
            else:
                end=pos-1
            pos=(begin+end)/2
        return None





if __name__=="__main__":
    ip_obj=ip_parse_t("../data/ip.all","../data/region.txt")
    start=time.time()
    ip="218.203.195.114"
    result_list=ip_obj.search(ip)
    print result_list[-1],result_list[-2]
    end=time.time()
    print end-start,ip


