#!/usr/local/bin/python
# -*- coding: utf-8 -*-
               
__version__ = "1.0.0.0"
import sys
import ConfigParser
import struct
import socket
import time
import urlparse
import threading
from datetime import datetime
import json
import msg_pb2
import types

reload(sys)

sys.setdefaultencoding('utf-8')

class Client:
    def __init__(self):
        self.ip = None
        self.port = None
        self.time = None

    def init(self,cf):     
        self.ip = cf["host"]
        self.port = cf["port"]
        self.time = cf["timeout"]

    def send_and_recv(self, req_msg, timeout=30):
        pack=req_msg.SerializeToString()
        plen = len(pack)
        hid = 0
        log_id = 1
        version = 2
        magic_num = 0xfb709394
        provider1 = 0x0000
        provider2 = 0x0031
        head = struct.pack("HHHQQIII", hid, version, log_id, provider1, provider2, magic_num, 0, plen)
        clisock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clisock.settimeout(timeout)
        clisock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) 
        #try:
        clisock.connect((self.ip, self.port))
        clisock.send(head)
        clisock.send(pack)
        return self.recv_all(clisock)
        #except Exception as e:
        #    print e
        #    return e
        
    def recv_all(self, clisock):
        head = clisock.recv(36, socket.MSG_WAITALL)
        body_len = self.parse_nshead(head)
        dat = clisock.recv(body_len)
        rev_len = len(dat)
        while rev_len < body_len:
            dat += clisock.recv(body_len - rev_len)
            rev_len = len(dat)
        #mcpack.set_default_version(mcpack.mcpackv2)
        #bodydict = mcpack.loads(dat)
        #print body_len
        res_msg=msg_pb2.ad_res_t()
        res_msg.ParseFromString(dat)
        #array=res_msg.predict_result
        #for obj in array:
         #   print obj.prob,obj.trade_id
        return res_msg

    def parse_nshead(self, header):
        (id, verison, log_id, provider, magic_num, reserved, body_len) = struct.unpack("2HI16s3I", header)
        return body_len

if __name__ == '__main__':
    cf={}
    cf["host"] = "127.0.0.1"
    cf["port"] = 23351
    cf["timeout"] = 0.001
    string="垃圾"
    client = Client(cf)
    req_msg=msg_pb2.ad_req_t()
    req_msg.session_id="3434"
    req_msg.req_json_str="34"
    start=time.time()
    result = client.send_and_recv(req_msg, 100000)
    end=time.time()
    print end-start
