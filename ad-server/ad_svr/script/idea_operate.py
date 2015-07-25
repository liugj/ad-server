#!/usr/bin/env
# -*- coding: utf-8 -*-

import logging
from process_file import file_process_t

class idea_operator_t:
    def __init__(self,idea_operator_file):
        self.idea_operator_dict={}
        fp=open(idea_operator_file,"r")
        line_cnt=0
        file_obj=file_process_t()
        for line in fp:
            data_list=line.rstrip("\r\n").split("\t")
            line_cnt+=1
            if line_cnt==1:
                file_obj.init_header(data_list)
                continue
            idea_id=file_obj.get_value("idea_id",data_list)
            basic_bid=float(file_obj.get_value("basic_bid",data_list))
            thr=float(file_obj.get_value("thr",data_list))
            self.idea_operator_dict[idea_id]={"basic_bid":basic_bid,"thr":thr}
        fp.close()
       
    

