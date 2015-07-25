#!/usr/local/bin/python
# -*- coding: utf-8 -*- 

import logging
import math

class predict_model_t:
    def __init__(self,model_file):
        self.weight_list=[]
        fp=open(model_file,"r")
        line_cnt=0
        for line in fp:
            line_cnt+=1
            line=line.rstrip("\r\n")
            if line_cnt<7:
                continue
            weight=float(line)
            self.weight_list.append(weight) 
        fp.close()

    def predict(self,fea_str):
        fea_list=fea_str.split(" ")
        sum=0
        for fea_info in fea_list:
            fea_id=int(fea_info.split(":")[0])
            if fea_id>len(self.weight_list)-1:
                continue
            weight=self.weight_list[fea_id-1]
            sum+=weight
        prob=1-1.0/(1+math.exp(-sum))
        return  prob

if __name__=="__main__":
    obj=predict_model_t("../data/model1")
    print obj.predict("3:1 15:1 20:1 27472:1 27473:1")
