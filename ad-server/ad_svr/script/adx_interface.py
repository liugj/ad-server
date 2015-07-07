#!/usr/bin/env
# -*- coding: utf-8 -*-
import logging
import json
from adx_id_map import adx_id_map

def get_value(json_dict,key):
    if json_dict==None:
        return None
    if key in json_dict:
        return json_dict[key]
    return None   

class mongo_v1_2:
    def __init__(self,adx_id_map):
        self.adx_id_map=adx_id_map
        self.version="mongo_v1_2"
        pass
                
    def parse_bid_request(self,req):
        
        pass

    def create_bid_response(self,res_dict):
        pass
        


class mongo_v1_3_1:
    def __init__(self,adx_id_map):
        self.adx_id_map=adx_id_map
        self.version="mongo_v1_3_1"
        pass
                
    def parse_bid_request(self,adx_data_dict):
        parse_req_dict={}
        #process device info
        device_dict=get_value(adx_data_dict,"device")
        ip=get_value(device_dict,"ip")
        manufactory=get_value(device_dict,"make")
        mongo_device_id=get_value(device_dict,"devicetype")
        device_id=get_value(self.adx_id_map.adx_id_dict["device"],str(mongo_device_id))
        density=get_value(device_dict,"density")
        mongo_network=get_value(device_dict,"connectiontype")
        network=get_value(self.adx_id_map.adx_id_dict["network"],str(mongo_network))
        orientation=get_value(device_dict,"orientation")
        mongo_operator=get_value(device_dict,"carrier")
        operator=get_value(self.adx_id_map.adx_id_dict["operator"],mongo_operator)
        parse_req_dict["ip"]=ip
        parse_req_dict["manufactory"]=manufactory
        parse_req_dict["device"]=device_id
        parse_req_dict["network"]=network
        parse_req_dict["operator"]=operator
        #process app info
        app_dict=get_value(adx_data_dict,"app")
        app_name=get_value(app_dict,"name")
        app_id=get_value(app_dict,"aid")
        mongo_class_list=get_value(app_dict,"cat")
        class_list=[]
        for mongo_class_id in mongo_class_list:
            class_id=get_value(self.adx_id_map.adx_id_dict["classification"],mongo_class_id)
            class_list.append(class_id)
        parse_req_dict["class_list"]=class_list
        parse_req_dict["mongo_class_list"]=mongo_class_list
        #process imp info        
        imp_dict=get_value(adx_data_dict,"imp")[0]
        instl=get_value(imp_dict,"instl")
        #get ad type
        if instl==0:
            ad_type="banner"
        elif instl==1:
            if orientation==1:
                ad_type="plaqueX"
            elif orientation==2:
                ad_type="plaqueY"
            else:
                ad_type="unknown"
        else:
            ad_type="unknown"
        parse_req_dict["type"]=[]
        combine_key=ad_type+"_"+device_id
        type=get_value(self.adx_id_map.search_type_dict,combine_key)
        parse_req_dict["type"].append(type)
        if ad_type=="banner":
            parse_req_dict["type"].append("banner_text")
        #get ad size
        ad_width=int(get_value(imp_dict,"w"))
        ad_height=int(get_value(imp_dict,"h"))
        available_size_list=[]
        if ad_type=="banner":
            size=str(ad_width)+"x"+str(ad_height)
            size_id=get_value(self.adx_id_map.size_invert_dict,size)
            available_size_list.append(size_id)
            if density>1.5:
               high_density_size=str(ad_width*2)+"x"+str(ad_height*2)
               size_id=get_value(self.adx_id_map.size_invert_dict,high_density_size)
               available_size_list.append(size_id)
        elif ad_type=="plaqueX" or ad_type=="plaqueY":
            sub_dict=self.adx_id_map.type_size_dict[type]
            if sub_dict!=None:
                for size_id in sub_dict:
                    available_size_list.append(size_id)
        parse_req_dict["available_size"]=available_size_list         
        logging.debug("%s" %(parse_req_dict))
        return parse_req_dict        
       
    def create_bid_response(self,res_dict):
        pass

class adx_interface_t:
    def __init__(self,adx_id_map):
        self.adx_id_map=adx_id_map
        self.interface_dict={}
        obj=mongo_v1_3_1(self.adx_id_map)   
        self.interface_dict["mongo_v_1_3_1"]=obj
        obj=mongo_v1_2(self.adx_id_map)
        self.interface_dict["mongo_v_1_2"]=obj

    def get_obj(self,channel):
        if channel in self.interface_dict:
            return self.interface_dict[channel]
        return None    

        
