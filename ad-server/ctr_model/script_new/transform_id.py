#!/usr/bin/env
# -*- coding: utf-8 -*-
import logging

class transform_id_t:
    def __init__(self,fea_id_file):
        self.fea_id_file=fea_id_file
        self.fea_id_dict={}
        self.max_id=0
        fp=open(fea_id_file,"r")
        for line in fp:
            line=line.rstrip("\r\n").split("\t")
            fea_value=line[0]
            fea_id=int(line[1])
            self.fea_id_dict[fea_value]=fea_id
            if fea_id>self.max_id:
                self.max_id=fea_id
        self.max_id+=1
    
    def get_id(self,fea_value):
        if fea_value in self.fea_id_dict:
            fea_id=self.fea_id_dict[fea_value] 
            return fea_id
        fea_id=self.max_id
        self.fea_id_dict[fea_value]=fea_id
        self.max_id+=1
        return fea_id
    
    def update_fea_file(self):
        fp=open(self.fea_id_file,"w")     
        for fea_value in self.fea_id_dict:
            fp.write("%s\t%d\n" %(fea_value,self.fea_id_dict[fea_value]))
                  
        fp.close()
