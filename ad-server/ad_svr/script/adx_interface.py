#!/usr/bin/env
# -*- coding: utf-8 -*-
import logging
import json
from adx_id_map import adx_id_map
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

g_text_template='''
<meta http-equiv='Content-Type' content='text/html; charset=UTF-8' /><style type='text/css'>*{padding:0px;margin:0px;} a:link{text-decoration:underline;}</style><a href='#CLICK_URL#'><div style='width:320px;height:50px;'><table width="320" border="0" cellspacing="0" cellpadding="0"><tr height="50"><td height="50"align="center" style="color:blue;text-decoration: underline;">%s</td></tr></table></div></a>#IMP_TRACK#
'''

g_banner_template= '''
    <meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />
    <style type="text/css">
        *{
            padding:0;
            margin:0;
        }
        a:link{
            text-decoration:none;
        }
        a img{
            border:none 0;    
        }
        .ad {
           position: fixed;    
           display:block;
           width: 100%%;
           height: 100%%;
           overflow:hidden;
           text-align:center;
        }
        
    </style>
    <a href='#CLICK_URL#' class="ad">
        <img src="%s" alt="" width="100%%" height="100%%" />
    </a>#IMP_TRACK#
''';

g_plaque_template= '''
    <meta http-equiv='Content-Type' content='text/html; charset=UTF-8' />
    <style type="text/css">
        *{
            padding:0;
            margin:0;
        }
        a:link{
            text-decoration:none;
        }
        a img{
            border:none 0;    
        }
        .ad {
           display:block;
           width: 100%%;
           height: 100%%;
           overflow:hidden;
           text-align:center;
           overflow:hidden;
        }
        .ad img{
           width:100%%;
           height:100%%;
        }

        
    </style>
    <a href='#CLICK_URL#' class="ad">
       <img src="%s" alt="" width="%dpx" height="%dpx" />
    </a>#IMP_TRACK#
''';


def get_value(json_dict,key):
    if json_dict==None:
        return None
    if key in json_dict:
        return json_dict[key]
    return None   

class mongo_v1_2:
    def __init__(self,adx_id_map,conf):
        self.adx_id_map=adx_id_map
        self.version="mongo_v1_2"
        pass
                
    def parse_bid_request(self,req):
        
        pass

    def create_bid_response(self,res_dict):
        pass
        


class mongo_v1_3_1:
    def __init__(self,adx_id_map,conf):
        self.adx_id_map=adx_id_map
        self.version="mongo_v1_3_1"
        self.conf=conf
        pass
                
    def parse_bid_request(self,adx_data_dict):
        parse_req_dict={}
        #process device info
        device_dict=get_value(adx_data_dict,"device")
        ip=get_value(device_dict,"ip")
        manufactory=get_value(device_dict,"make")
        mongo_device_type=get_value(device_dict,"devicetype")
        device_type=get_value(self.adx_id_map.adx_id_dict["device"],str(mongo_device_type))
        dpid=get_value(device_dict,"dpid")
        density=get_value(device_dict,"density")
        mongo_network=get_value(device_dict,"connectiontype")
        network=get_value(self.adx_id_map.adx_id_dict["network"],str(mongo_network))
        orientation=get_value(device_dict,"orientation")
        mongo_operator=get_value(device_dict,"carrier")
        operator=get_value(self.adx_id_map.adx_id_dict["operator"],mongo_operator)
        parse_req_dict["ip"]=ip
        parse_req_dict["manufactory"]=manufactory
        parse_req_dict["device_type"]=device_type
        parse_req_dict["network"]=network
        parse_req_dict["operator"]=operator
        parse_req_dict["dpid"]=dpid
        
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
            if orientation==2:
                ad_type="plaqueX"
            elif orientation==1:
                ad_type="plaqueY"
            else:
                ad_type="unknown"
        else:
            ad_type="unknown"
        parse_req_dict["impid"]=imp_dict["impid"]
        parse_req_dict["type"]=[]
        combine_key=ad_type+"_"+device_type
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
       
    def create_adx_response(self,parse_req_dict,idea_id,idea_json,adx_req_dict,bid):
        adx_response_dict={}
        ext_obj={}
        adx_response_dict["id"]=adx_req_dict["id"]
        if bid==0:
            adx_response_dict["nbr"]=0
            adx_response_dict["seatbid"]=[]
            return adx_response_dict
        logging.debug("laji")
        seat_obj_list=[]
        seat_obj={}
        bid_obj_list=[]
        bid_obj={}
        req_imp_dict=adx_req_dict["imp"][0]
        ad_type=req_imp_dict["instl"]    
        imp_id=req_imp_dict["impid"]
        bid_obj["impid"]=imp_id
        bid_obj["price"]=bid
        bid_obj["adid"]=idea_id
        dsp_info_dict={}
        dsp_info_dict["device_type"]=parse_req_dict["device_type"]
        dsp_info_dict["network"]=parse_req_dict["network"]
        dsp_info_dict["operator"]=parse_req_dict["operator"]
        dsp_info_dict["classification"]=",".join(parse_req_dict["class_list"])
        dsp_info_dict["dpid"]=parse_req_dict["dpid"]
    
        dsp_info_dict["region"]=str(parse_req_dict["region"][2])+","+str(parse_req_dict["region"][3])
        dsp_url=""
        for key,value in dsp_info_dict.items():
            dsp_url+=str(key)+"*"+str(value)+"$$$"
        dsp_url=dsp_url.rstrip("$$$")    
        #set url
        bid_obj["nurl"]=self.conf.get("url","nurl")+imp_id+"$$$win_price*#WIN_PRICE#"+"$$$idea_id*"+idea_id
        bid_obj["cturl"]=[self.conf.get("url","cturl")+imp_id+"$$$idea_id*"+idea_id]
        bid_obj["iurl"]=self.conf.get("url","iurl")+imp_id+"$$$idea_id*"+idea_id+"$$$"+dsp_url
        download_aurl=self.conf.get("url","download_aurl")+imp_id+"$$$idea_id*"+idea_id
        install_aurl=self.conf.get("url","install_aurl")+imp_id+"$$$idea_id*"+idea_id
        open_aurl=self.conf.get("url","open_aurl")+imp_id+"$$$idea_id*"+idea_id
        bid_obj["aurl"]=download_aurl+"||"+install_aurl+"||"+open_aurl
        bid_obj["crid"]=idea_id
        #set adm
        idea_ad_type=idea_json["type"]
        if idea_ad_type=="banner_text":
            text=idea_json["alt"]
            adm=g_text_template %(text)
        elif idea_ad_type=="banner_android" or idea_ad_type=="banner_iphone" or idea_ad_type=="banner_ipad":
            img_src="http://mobile-ad.shoozen.net/"+idea_json["src"]
            adm=g_banner_template %(img_src)        
        else:
            img_src="http://mobile-ad.shoozen.net/"+idea_json["src"]
            size_id=idea_json["size_id"]
            size_json_dict=self.adx_id_map.size_dict[size_id]    
            size_str=size_json_dict["size_str"]
            is_full=size_json_dict["is_full"]
            width=int(size_str.split("x")[0])
            height=int(size_str.split("x")[1])
            adm=g_plaque_template %(img_src,width,height)
            bid_obj["adw"]=width
            bid_obj["adh"]=height
            if is_full=="N":
                ext_obj["instl"]=1
            else:
                ext_obj["instl"]=2
        bid_obj["adm"]=adm
        #set ctype
        click_action_id=idea_json["click_action_id"]
        bid_obj["ctype"]=int(click_action_id)   
        bid_obj["curl"]=idea_json["link"]           
        #download
        if click_action_id=="2":
            app_name=idea_json["name"]
            ext_obj["apkname"]=app_name
            bid_obj["cbundle"]=idea_json["link_text"]
        elif click_action_id=='5':
            bid_obj["curl"]="tel://"+idea_json["link"]           
        parse_req_dict["src"]=idea_json["src"]
        parse_req_dict["alt"]=idea_json["alt"]
        bid_obj["ext"]=ext_obj
        bid_obj_list.append(bid_obj)   
        seat_obj["bid"]=bid_obj_list
        seat_obj_list.append(seat_obj)
        adx_response_dict["seatbid"]=seat_obj_list
        #logging.info("adx response:%s" %(adx_response_dict))
        return adx_response_dict

class adx_interface_t:
    def __init__(self,adx_id_map,conf):
        self.adx_id_map=adx_id_map
        self.interface_dict={}
        obj=mongo_v1_3_1(self.adx_id_map,conf)   
        self.interface_dict["mongo_v_1_3_1"]=obj
        obj=mongo_v1_2(self.adx_id_map,conf)
        self.interface_dict["mongo_v_1_2"]=obj

    def get_obj(self,channel):
        if channel in self.interface_dict:
            return self.interface_dict[channel]
        return None    

        
