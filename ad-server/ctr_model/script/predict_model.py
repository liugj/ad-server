#!/usr/local/bin/python
# -*- coding: utf-8 -*- 

import ConfigParser
import csv
import math
import re
import sys
import time
import logging

class predict_model_t:
	def __init__(self):

		
		self.label_dict = {}

		self.weight_dict = {}

		self.fea_num = 0
	
	        self.nr_class=0 

                self.first_label_id=0

                self.model_dict={}
                self.label_list=[]

	def load_model(self,model_file):
	     fp=open(model_file,"r")
             line_cnt=0
             fea_id=1
             for line in fp:
                 line_cnt+=1
                 line=line.rstrip("\r\n").rstrip(' ').split(' ')
                 if line_cnt==3:
                     for i in range(1,len(line)):
                         label_id=int(line[i])
                         sub_dict={}
                         self.label_list.append(label_id)
                         self.model_dict[label_id]=sub_dict
                 if line_cnt>=7:
                     for i in range(0,len(line)):
                         label_id=self.label_list[i]
                         sub_dict=self.model_dict[label_id]
                         weight=float(line[i])
                         if weight!=0:
                             sub_dict[fea_id]=weight
                             self.model_dict[label_id]=sub_dict
                     fea_id+=1
             fp.close()

   			
	def predict_prob(self,string):
		#7 4:1.100000 5:1.100000 6:1.000000 7:1.000000 8:1.000000
		items = string.rstrip('\r\n').strip(" ").split(' ')
                fea_list=[]
                for weight_info in items:
                    pair=weight_info.split(':')    
                    if len(pair)!=2:
                       continue
                    fea_id=int(pair[0])
                    weight=float(pair[1])
                    fea_list.append([fea_id,weight])
                result_list=[]
                prob_sum=0
               
                for label_id  in self.model_dict:
                     sum=0
                     sub_dict=self.model_dict[label_id]
                     for [fea_id,weight] in fea_list:
                         if not(fea_id in sub_dict):
                             continue
                         model_weight=sub_dict[fea_id]
                         sum+=weight*model_weight
                         #print fea_id,weight,model_weight,label_id
                     prob=1.0/(1+math.exp(-sum))
                     prob_sum+=prob
                     result_list.append([label_id,prob])
                for i in range(0,len(result_list)):
                     [label_id,prob]=result_list[i]
                     result_list[i]=[label_id,prob/prob_sum]
                result_list.sort(lambda x,y:cmp(x[1],y[1]),reverse=True)
		return result_list

	

if __name__=="__main__":
	#if len(sys.argv) < 4:
#		print 'Usage: %s test_file model output'%(sys.argv[0])
#		sys.exit(1)
    start=time.time()
    g_predict_data = predict_model_t()
    g_predict_data.load_model(sys.argv[1])
    end=time.time()
    print end-start
    print 'after loading model'
    print g_predict_data.predict_prob('512:1.2')
	#predict(g_predict_data,sys.argv[1],sys.argv[2],sys.argv[3])
