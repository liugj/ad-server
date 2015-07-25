#!/usr/bin/env
# -*- coding: utf-8 -*-
import logging
import sys
from process_file import file_process_t
import datetime

def process(input_file,output_sql):
    now_time_list=datetime.datetime.now().strftime("%H:%M:%S").split(":")
    date_today=datetime.datetime.now().strftime("%Y-%m-%d")
    hour=int(now_time_list[0])
    minute=int(now_time_list[1])
    second=int(now_time_list[2])
    total_second=hour*3600+minute*60+second
    ratio=float(total_second)/86400
    
    input_fp=open(input_file,"r")
    sql_fp=open(output_sql,"w")
    file_obj=file_process_t()
    line_cnt=0
    sql_fp.write("use mis;\n")
    for ori_line in input_fp:
        data_list=ori_line.rstrip("\r\n").split("\t")
        line_cnt+=1
        if line_cnt==1:
            file_obj.init_header(data_list)
            continue
        idea_id=file_obj.get_value("id",data_list)
        budget=float(file_obj.get_value("budget",data_list))   
        available_budget=budget*ratio
        sql_fp.write("insert into consumptions(date,idea_id,smooth) values('%s','%s','%f') on DUPLICATE KEY update smooth='%f';\n" %(date_today,idea_id,available_budget,available_budget))

    input_fp.close()
    sql_fp.close()
    

def init():
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='[%Y-%m_%d %H:%M:%S]',
                filename='../log/update_smooth_charge.log',
                filemode='a')
    
if __name__=="__main__":
    init()
    input_file=sys.argv[1]
    output_sql=sys.argv[2]
    process(input_file,output_sql)


