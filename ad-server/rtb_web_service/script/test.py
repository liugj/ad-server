#!/usr/bin/python
# -*- coding: utf-8 -*-


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
           height:50px;
           overflow:hidden;
           text-align:center;
        }
        
    </style>
    <a href='#CLICK_URL#' class="ad">
        <img src="%s" alt="" width="%dpx" height="%dpx" />
    </a>#IMP_TRACK#
''';

size_str="728x90"
width=728
height=90
url="http://imgser.shoozen.net/20140814/"+size_str+".jpg"
print url
adm=html_banner_bian %(url,width,height)
print adm


