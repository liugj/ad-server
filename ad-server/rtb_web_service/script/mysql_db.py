#!/usr/bin/env
# -*- coding: utf-8 -*-
import MySQLdb
import logging


class mysql_db:
    #define internal variabels
    connect_obj=None
    
    #define function for connecting to db
    def establish_connection(self,host_ip,user_name,password,port_num):
        try:
            self.connect_obj=MySQLdb.connect(host=host_ip,user=user_name,passwd=password,port=port_num)
            self.connect_obj.set_character_set('utf8')
        except:
            return -1   
        return 0
    
    #define function for close connection to db
    def close_connection(self):
        self.connect_obj.close()
        
    #define SQL query to db and fetch result
    def sql_query(self,sql,db_name):
        try:
            self.connect_obj.select_db(db_name)
            cur=self.connect_obj.cursor()
            result_num=cur.execute(sql)
            result_array=cur.fetchall()
        except:
            return None
        return [result_num,result_array]


    def update_query(self,sql,db_name):
        try:
            self.connect_obj.select_db(db_name)
            cur=self.connect_obj.cursor()
            cur.execute(sql)
            self.connect_obj.commit()
        except Exception as e:
            logging.warning("error %s" %(e))
            return 0

    #dump function
    def dump(self,sql,db_name,output_file,max_num_once,split_ch):
            file=open(output_file,"w")
            self.connect_obj.select_db(db_name)
            cur=self.connect_obj.cursor()
            cur.execute("set names utf8")
            result_num=cur.execute(sql)
            offset=0
            while offset<result_num:
                result_array=cur.fetchmany(max_num_once)
                for i in range(0,len(result_array)):
                    sub_array=result_array[i]
                    output_line=""
                    for col in range(0,len(sub_array)):
                        string=str(sub_array[col])
                        string=string.replace('\n',' ')
                        string=string.replace('\t',' ')
                        #string=string.decode('gbk').encode('utf-8')
                        output_line+=string+split_ch
                    output_line=output_line.rstrip(split_ch)+'\n'
                    file.write(output_line)
                offset+=max_num_once
            return 0
            

