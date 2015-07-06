#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
import random
g_response_dict={}
g_nurl="http://online-rtb.shoozen.net/win_notice?id="
g_curl="http://monitor.shoozen.net/click?id="
g_iurl="http://monitor.shoozen.net/show?id="

g_img_list=["750x560","560x750","1024x768","1136x640","369x657","415x738","480x700","492x738","560x700","560x985","640x1136","657x369","700x480","700x560","738x415","738x492","768x1024","985x560"]
g_count=0
g_pad_banner_list=["728x90","468x60","320x50","300x250","640x100"]
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
           height: 100%%;
           overflow:hidden;
           text-align:center;
        }
        
    </style>
    <a href='#CLICK_URL#' class="ad">
        <img src="%s" alt="" width="100%%" height="100%%" />
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



def get_message(req_dict,bid_dict):
    if not("id" in req_dict):
        logging.warning("no id in req dict")
        return None
    id=req_dict["id"].encode('utf-8')
    if not("imp" in req_dict):
        logging.warning("no impid in req_dict")
        return None
    response_dict={}
    response_dict["id"]=id
    response_dict["bidid"]="0"
    bid_info_dict=bid_dict["response"]
    if not("result" in bid_info_dict) or len(bid_info_dict["result"])==0:
        response_dict["nbr"]=0
        return response_dict
    bid=bid_info_dict["result"]["bid"]
    idea_id=bid_info_dict["result"]["idea_id"]
    display_width=int(bid_info_dict["result"]["width"])
    display_height=int(bid_info_dict["result"]["height"])
    display_click_url=bid_info_dict["result"]["click_url"]
    display_img_url=bid_info_dict["result"]["img_url"]
    #loop for impid
    seat_obj_list=[]
    bid_obj_list=[]
    seat_obj={}
    if len(req_dict["imp"])!=1:
        return None
    for imp_obj in req_dict["imp"]:
        bid_obj={}
        try:
            imp_id=imp_obj["impid"].encode('utf-8')
            ad_type=0
            if "instl" in imp_obj:
                ad_type=imp_obj["instl"]    
            else:
                logging.warning("no instl in request body")

            bid_obj["impid"]=imp_id
            bid_obj["price"]=bid
            bid_obj["adid"]=idea_id
            bid_obj["nurl"]=g_nurl+imp_id+"=#WIN_PRICE#"+"&idea_id="+idea_id
            bid_obj["adm"]=""
            bid_obj["cid"]=idea_id
            bid_obj["crid"]=idea_id
            bid_obj["ctype"]=3
            #bid_obj["cbundle"]="5028_miller.apk"
            bid_obj["curl"]=g_curl+imp_id+"&idea_id="+idea_id
            bid_obj["iurl"]=g_iurl+imp_id+"&idea_id="+idea_id
            if ad_type==0:
                adm=html_banner_bian %(display_img_url)
                bid_obj["adm"]=adm
            else:
                bid_obj["adm"]=html_str_plaque_heng %(display_img_url,display_width,display_height)
                bid_obj["adw"]=display_width
                bid_obj["adh"]=display_height
        except Exception as err:
            logging.warning("encap failed[%s]" %(err))
            continue
        bid_obj_list.append(bid_obj)
    seat_obj["bid"]=bid_obj_list
    seat_obj["seat"]="1"
    seat_obj_list.append(seat_obj)
    response_dict["seatbid"]=seat_obj_list
    return response_dict
