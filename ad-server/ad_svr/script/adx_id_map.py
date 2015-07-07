#!/usr/bin/env
# -*- coding: utf-8 -*-

import logging
from process_file import file_process_t


class adx_id_map:
    def __init__(self,conf):
        self.adx_id_dict={}
        self.adx_id_file_dict={}
        self.adx_id_dict["device"]={}
        self.adx_id_file_dict["device"]=conf.get("file","device")
        
        self.adx_id_dict["network"]={}
        self.adx_id_file_dict["network"]=conf.get("file","network")

        self.adx_id_dict["classification"]={}
        self.adx_id_file_dict["classification"]=conf.get("file","classification")
        self.search_type_dict={}
        self.type_size_dict={}
        self.size_dict={}
        self.size_invert_dict={}
        for name in self.adx_id_file_dict:
            file_name=self.adx_id_file_dict[name]
            map_dict=self.adx_id_dict[name]
            fp=open(file_name,"r")
            file_obj=file_process_t()
            line_cnt=0
            for ori_line in fp:
                data_list=ori_line.rstrip("\r\n").split("\t")
                line_cnt+=1
                if line_cnt==1:
                    file_obj.init_header(data_list)
                    continue
                id=file_obj.get_value("id",data_list)
                adx=file_obj.get_value("adx",data_list)
                map_dict[adx]=id        

        fp=open(conf.get("file","sizes"),"r")
        file_obj=file_process_t()
        line_cnt=0
        for ori_line in fp:
            data_list=ori_line.rstrip("\r\n").split("\t")
            line_cnt+=1
            if line_cnt==1:
                file_obj.init_header(data_list)
                continue
            id=file_obj.get_value("id",data_list)
            width=file_obj.get_value("width",data_list)
            height=file_obj.get_value("height",data_list)
            size_str=width+"x"+height
            self.size_invert_dict[size_str]=id
            self.size_dict[id]=size_str
        fp=open(conf.get("file","type_size_join"),"r")
        file_obj=file_process_t()
        line_cnt=0
        for ori_line in fp:
            data_list=ori_line.rstrip("\r\n").split("\t")
            line_cnt+=1
            if line_cnt==1:
                file_obj.init_header(data_list)
                continue
            type_name=file_obj.get_value("name_en",data_list)
            ad_type=(type_name.split("_"))[0]
            device_id=file_obj.get_value("device_id",data_list)
            size_id=file_obj.get_value("size_id",data_list)
            combine_key=ad_type+"_"+device_id
            self.search_type_dict[combine_key]=type_name
            if type_name in self.type_size_dict:
                sub_dict=self.type_size_dict[type_name]
            else:
                sub_dict={}
            sub_dict[size_id]=1
            self.type_size_dict[type_name]=sub_dict    
            
        fp=open(conf.get("file","manual_operator"),"r")
        self.adx_id_dict["operator"]={}
        file_obj=file_process_t()
        line_cnt=0
        for ori_line in fp:
            data_list=ori_line.rstrip("\r\n").split("\t")
            line_cnt+=1
            if line_cnt==1:
                file_obj.init_header(data_list)
                continue
            code=file_obj.get_value("code",data_list)
            id=file_obj.get_value("id",data_list)
            self.adx_id_dict["operator"][code]=id
        fp.close()
