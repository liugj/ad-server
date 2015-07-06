#!/usr/bin/env
# -*- coding: utf-8 -*-
import logging
import json

class inverted_index_t:
    def __init__(self):
        self.inverted_dict={}
    
    def insert_data(self,key,value):
        if key in self.inverted_dict:
            value_list=self.inverted_dict[key]    
        else:
            value_list=[]
        value_list.append(value)
        self.inverted_dict[key]=value_list
    
    def search(self,key):
        if key in self.inverted_dict:
            return self.inverted_dict[key]
        else:
            return None       

    def dump(self,file_path):
        output_fp=open(file_path,"w")
        for key in self.inverted_dict:
            value_list=self.inverted_dict[key]
            value_str=",".join(value_list)
            output_fp.write("%s\t%s\n" %(key,value_str))
        output_fp.close()
       
class index_t:
    def __init__(self):
        self.index_dict={}

    def insert_data(self,key,section_name,value):
        if key in self.index_dict:
            value_dict=self.index_dict[key]
        else:
            value_dict={}
        value_dict[section_name]=value
        self.index_dict[key]=value_dict
    
    def search(self,key):
        if key in self.index_dict:
            return self.index_dict[key]
        else:
            return None       

    def dump(self,file_path):
        output_fp=open(file_path,"w")
        for key in self.index_dict:
            value_dict=self.index_dict[key]
            output_fp.write("%s\t%s\n" %(key,json.dumps(value_dict)))
        output_fp.close()

    
class map_t:
    def __init__(self):
        self.data_dict={}

    def insert_data(self,map_name,key,value):
        if map_name in self.data_dict:
            sub_dict=self.data_dict[map_name]
        else:
            sub_dict={}
        sub_dict[key]=value
        self.data_dict[map_name]=sub_dict
    
    def search(self,map_name,key):
        if not(map_name in self.data_dict):
            logging.warning("no such map name[%s]" %(map_name))
            return None
        sub_dict=self.data_dict[map_name]
        if key in sub_dict:
            return sub_dict[key]
        return None

 
                   

class data_factory_t:
    def __init__(self,product_name):
        self.product_name=product_name
        self.data_obj=None

    def create_product(self):
        if self.product_name=="map":
            self.data_obj=map_t()
        elif self.product_name=="index":
            self.data_obj=index_t()
        elif self.product_name=="inverted_index":
            self.data_obj=inverted_index_t()
        return self.data_obj

class data_factory_mgr_t:
    def __init__(self):
        self.data_product_dict={}

    def insert_data_obj(self,name,data_obj):
        pass       
    

