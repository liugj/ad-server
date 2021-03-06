#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
import random
g_response_dict={}
g_nurl="http://rtb.shoozen.net/win_notice?id="
g_curl="http://monitor.shoozen.net/click?id="
g_iurl="http://monitor.shoozen.net/show?id="

g_img_list=["750x560","560x750","1024x768","1136x640","369x657","415x738","480x700","492x738","560x700","560x985","640x1136","657x369","700x480","700x560","738x415","738x492","768x1024","985x560"]
g_count=0
g_pad_banner_list=["728x90","468x60","320x50","300x250"]
g_banner_set=set(g_pad_banner_list)



html_banner_bian= '''
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
           height:100%%;
           overflow:hidden;
           text-align:center;
        }
        
    </style>
    <a href='#CLICK_URL#' class="ad">
        <img src="%s" alt="" width="%dpx" height="%dpx" />
    </a>#IMP_TRACK#
''';
#erer


html_str_plaque_shu= '''
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
           height:100%%;
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
     <img src="http://imgser.shoozen.net/20140806/1fbab945e0f1fe6dab22904bd460773c5.png" alt="" width="480px" height="700px" />
    </a>#IMP_TRACK#
''';
     #   <img src="http://imgser.shoozen.net/20140728/120c005590bc82ba52eeb84d629863866.jpg" alt="" width="320px" height="50px" />

html_str_plaque_heng= '''
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
        #<img src="http://imgser.shoozen.net/20140806/1a2e629d783e739b263146bd06db8f03e.png" alt="" width="700px" height="480px" />


g_banner = '''
    .ad {
        position: fixed;    
        display:block;
        width: 100%;
        height:%dpx;
        overflow:hidden;
        text-align:center;
    }
''';

g_plaque = '''
    .ad {
        position: fixed;    
        display:block;
        width: %dpx;
        height:%dpx;
        overflow:hidden;
        top:50%;
        left:50%;
        text-align:center;
        margin-top:-%dpx;
        margin-left:-%dpx;
    }
''';

html_str_total= '''
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
           width: 100%;
           height: 100%;
           overflow:hidden;
           text-align:center;
        }

        
    </style>
    <a href='#CLICK_URL#' class="ad">
        <img src="http://imgser.shoozen.net/20140806/1a2e629d783e739b263146bd06db8f03e.png" alt="" width="700px" height="480px" />
    </a>#IMP_TRACK#
''';



def bid_response(req_dict):
    global g_count
    if not("id" in req_dict):
        logging.warning("no id in req dict")
        return None
    id=req_dict["id"]
    if not("imp" in req_dict):
        logging.warning("no impid in req_dict")
        return None
    response_dict={}
    response_dict["id"]=id
    response_dict["bidid"]="0"
    #loop for impid
    seat_obj_list=[]
    bid_obj_list=[]
    seat_obj={}
    for imp_obj in req_dict["imp"]:
        bid_obj={}
        try:
            imp_id=imp_obj["impid"]
            ad_type=0
            if "instl" in imp_obj:
                ad_type=imp_obj["instl"]    
            else:
                logging.warning("no instl in request body")

            bid_obj["impid"]=imp_id
            bid_obj["price"]=26000
            bid_obj["adid"]=234
            bid_obj["nurl"]=g_nurl+id+"=#WIN_PRICE#"
            bid_obj["adm"]=""
            bid_obj["cid"]="111"
            bid_obj["crid"]="112"
            bid_obj["curl"]=g_curl+imp_id
            bid_obj["iurl"]=g_iurl+imp_id
            if ad_type==0:
                width=imp_obj["w"]
                height=imp_obj["h"]
                logging.info("banner:width[%d] height[%d]" %(width,height))
                size_str=str(width)+"x"+str(height)
                if not(size_str in g_banner_set):
                    logging.warning("invalid size [%s]" %(size_str))
                    return "error"
                url="http://imgser.shoozen.net/20140813/"+size_str+".jpg"
                adm=html_banner_bian %(height,url,width,height)
                bid_obj["adm"]=adm
            else:
                if "device" in req_dict:
                     orientation=1
                     if "orientation" in req_dict["device"]:
                         orientation=req_dict["device"]["orientation"]
                     if "sw" in req_dict["device"] and "sh" in req_dict["device"]:
                         if orientation==1:
                             adw_max=req_dict["device"]["sw"]
                             adh_max=req_dict["device"]["sh"]
                         else:
                             adh_max=req_dict["device"]["sw"]
                             adw_max=req_dict["device"]["sh"]
                         for count_temp in range(0,len(g_img_list)):
                             idx=g_count%len(g_img_list)                        
                             size_list=g_img_list[idx].split("x")
                             width=int(size_list[0])
                             height=int(size_list[1])
                             if width<adw_max and height<adh_max:
                                 break
                             g_count+=1
                         url="http://imgser.shoozen.net/20140813/"+g_img_list[idx]+".jpg"
                         bid_obj["adm"]=html_str_plaque_heng %(url,width,height)
                         bid_obj["adw"]=width
                         bid_obj["adh"]=height
                         device_type=req_dict["device"]["devicetype"]
                         if device_type==3 or device_type==1:
                             if orientation==1:
                                 if device_type==3:
                                     width=560
                                     height=750
                                 else:
                                     width=480
                                     height=700
                                 url="http://imgser.shoozen.net/20140813/%dx%d.jpg" %(width,height)

                                 bid_obj["adm"]=html_str_plaque_heng %(url,width,height)
                                 bid_obj["adw"]=width
                                 bid_obj["adh"]=height
                             else:
                                 if device_type==3:
                                     width=750
                                     height=560
                                 else:
                                     width=700
                                     height=480
                                 url="http://imgser.shoozen.net/20140813/%dx%d.jpg" %(width,height)
                                
                                 bid_obj["adm"]=html_str_plaque_heng %(url,width,height)
                                 bid_obj["adw"]=width
                                 bid_obj["adh"]=height
                                      
                         g_count+=1
                         #logging.debug("orientation:%d adw:%d adh:%d" %(orientation,bid_obj["adw"],bid_obj["adh"]))
        except Exception as err:
            logging.warning("encap failed[%s]" %(err))
            continue
        bid_obj_list.append(bid_obj)
    seat_obj["bid"]=bid_obj_list
    seat_obj["seat"]="1"
    seat_obj_list.append(seat_obj)
    response_dict["seatbid"]=seat_obj_list
    return response_dict
