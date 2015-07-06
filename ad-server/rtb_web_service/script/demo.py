# -*- coding: utf-8 -*- 
html = '''
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
        %s
    </style>
    <a href="http://lp.shoozen.net" class="ad">
        <img src="http://imgser.shoozen.net/%s" alt="" width="%dpx" height="%dpx" />
    </a>
''';

# banner css 
banner = '''
    .ad {
        position: fixed;    
        display:block;
        width: 100%%;
        overflow:hidden;
        text-align:center;
        height:%dpx;
    }
''';

# plaque css
plaque = '''
    .ad {
        position: fixed;    
        display:block;
        width: %dpx;
        height:%dpx;
        overflow:hidden;
        top:50%%;
        left:50%%;
        text-align:center;
        margin-top:-%dpx;
        margin-left:-%dpx;
    }
''';

############### 这部分代码自己实现 ####################

#从数据库获取 idea
idea = {
    'idea_type': 'banner',
    'img': 'http://www.google.com',
}

# 根据 idea 的size字段获取尺寸
size = {
    'width': 1024,
    'height': 768
}
#########################################################

ideaType = {
    'banner':  banner % (size['height']),
    'plaque': plaque % (size['width'], size['height'], size['width'] / 2, size['height'] / 2),
}

# 生成 adm 片段
adm = html % (ideaType[idea['idea_type']], idea['img'], size['width'], size['height']);
print adm;
