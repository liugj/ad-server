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
        
