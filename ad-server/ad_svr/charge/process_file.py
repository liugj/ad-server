#!/usr/bin/env
# -*- coding: utf-8 -*-

import logging
class file_process_t:
    def __init__(self):
        self.header_dict={}
       
    def init_header(self,header_list):
        for i in range(0,len(header_list)):
            name=header_list[i]
            self.header_dict[name]=i
        
    def get_value(self,name,data_list):
        if not(name in self.header_dict):
            return None
        idx=self.header_dict[name]
        return data_list[idx]

def build_map(file_path,data_obj,key_name,value_name,map_name):
    fp=open(file_path,"r")
    file_obj=file_process_t()   
    line_cnt=0
    for ori_line in fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            flle_obj.init_header(data_list)             
            continue
        key_data=file_obj.get_value(key_name,data_list)
        value_data=file_obj.get_value(value_name,data_list)
        data_obj.insert_data(key_data,map_name,key_data,value_data)
    fp.close()

def build_inverted_index(file_path,data_obj,key_name,value_name):
    fp=open(file_path,"r")
    file_obj=file_process_t()   
    line_cnt=0
    for ori_line in fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            flle_obj.init_header(data_list)
            continue
        key_data=file_obj.get_value(key_name,data_list)
        value_data=file_obj.get_value(value_name,data_list)
        data_obj.insert_data(key_data,value_data)
    fp.close()

def build_index(file_path,data_obj,key_name,section_name,value):
    fp=open(file_path,"r")
    file_obj=file_process_t()   
    line_cnt=0
    for ori_line in fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            flle_obj.init_header(data_list)
            continue
        key_data=file_obj.get_value(key_name,data_list)
        value_data=file_obj.get_value(value_name,data_list)
        data_obj.insert_data(key_data,section_name,value_data)
    fp.close()
    
