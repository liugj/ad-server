#!/usr/bin/env
# -*- coding: utf-8 -*-
import logging
import types
def get_value(data_dict,key):
    if data_dict==None:
        return None
    if key in data_dict:
        return data_dict[key]
    return None
    
class filter_t:
    def __init__(self,ridx_mgr_dict):
        self.ridx_mgr_dict=ridx_mgr_dict

    def merge_list(self,list1,list2):
        pass
    
    def search_ridx(self,parse_req_dict,data_name,ridx_name):
        result_list=[]
        data=parse_req_dict[data_name]
        list1=[]
        if type(data) is types.ListType:
            for data_element in data:
                list_temp=self.ridx_mgr_dict[ridx_name].search(data_element)
                if list_temp!=None:
                    list1+=list_temp
        else:
            list1=self.ridx_mgr_dict[ridx_name].search(data)
        list2=self.ridx_mgr_dict[ridx_name].search("0")
        if list1!=None:
            result_list+=list1
        if list2!=None:
            result_list+=list2
        return result_list
            
    def get_overlap(self,list1,list2):
        uniq_dict={}
        result_list=[]
        for data in list1:
            uniq_dict[data]=1
        for data in list2:
            if data in uniq_dict:
                result_list.append(data)
        return result_list

    def filter(self,parse_req_dict):
        result_id_list=[]
        #type
        result_id_list=self.search_ridx(parse_req_dict,"type","type")
        #size
        ret_list=self.search_ridx(parse_req_dict,"available_size","size")
        result_id_list=self.get_overlap(result_id_list,ret_list)
        #network
        ret_list=self.search_ridx(parse_req_dict,"network","idea_network")
        result_id_list=self.get_overlap(result_id_list,ret_list)
        #device
        ret_list=self.search_ridx(parse_req_dict,"device","device_idea")
        result_id_list=self.get_overlap(result_id_list,ret_list)
        #media class
        ret_list=self.search_ridx(parse_req_dict,"class_list","classify_idea")
        result_id_list=self.get_overlap(result_id_list,ret_list)
        #operate
        ret_list=self.search_ridx(parse_req_dict,"operator","idea_operator")
        result_id_list=self.get_overlap(result_id_list,ret_list)
        #ban
        ret_list=self.search_ridx(parse_req_dict,"class_list","ban_idea")
        dict_temp={}
        for idea_id in result_id_list:
            dict_temp[idea_id]=1
        for idea_id in ret_list:
            if idea_id in dict_temp:
                del dict_temp[idea_id]
        result_id_list=[]
        for idea_id in dict_temp:
            result_id_list.append(idea_id)
        logging.debug("result_id_list:%s" %(result_id_list))
        
        
