#!/usr/bin/env
# -*- coding: utf-8 -*-

import logging
import datetime
from extract_feature import extract_feature_t
class rank_bid_t:
    def __init__(self,extract_fea_obj,model_obj,operator_obj):
        self.extract_fea_obj=extract_fea_obj
        self.model_obj=model_obj
        self.operator_obj=operator_obj
        self.single_fea_list=["region","app","time","app_type","manufacture"]
        self.combine_fea_list=[]
        
    def rank_bid(self,adx_req_dict,idea_list,idea_idx_dict):
        #for idea_id in idea_list:
        time_str=datetime.datetime.now().strftime("%H:%M:%S")
        logging.debug("%s %s" %(time_str,adx_req_dict))
        
        (fea_dict,fea_id_str)=self.extract_fea_obj.extract_feature(time_str,adx_req_dict,self.single_fea_list,self.combine_fea_list)    
        prob=self.model_obj.predict(fea_id_str)
        logging.debug("%s %s %f" %(fea_dict,fea_id_str,prob))
        result_list=[]
        for idea_id in idea_list:
            if idea_id in self.operator_obj.idea_operator_dict:
                operator_dict=self.operator_obj.idea_operator_dict[idea_id]
                logging.debug("thr:%f %f" %(prob,operator_dict["thr"]))
                if prob<operator_dict["thr"]:
                    continue
                bid=int(operator_dict["basic_bid"]*10000)
                result_list.append([idea_id,bid])
        logging.debug("selected ad:%s" %(result_list))
        result_list.sort(lambda x,y:cmp(x[1],y[1]),reverse=True)
        if len(result_list)>0:
            return result_list[0]
        else:
            return [0,0]
