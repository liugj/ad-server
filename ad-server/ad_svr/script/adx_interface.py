#!/usr/bin/env
# -*- coding: utf-8 -*-
import logging
import json
from adx_id_map import adx_id_map


class mongo_v1_2:
    def __init__(self,adx_id_map):
        self.adx_id_map=adx_id_map
        pass
                
    def parse_bid_request(self,req):
        
        pass

    def create_bid_response(self,res_dict):
        pass
        


class mongo_v1_3_1:
    def __init__(self,adx_id_map):
        self.adx_id_map=adx_id_map
        pass
                
    def parse_bid_request(self,req):
        pass

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

        
