#!/usr/bin/env python
# coding:utf-8

import socket
import json
import time
#import datetime
#import struct
import commands

class ZbxSender(object):
    def __init__(self,server = '127.0.0.1',host = '127.0.0.1',port = 10051,config = None):
        if config is not None:
            import re
            reServer = re.compile("^Server\s*=\s*(\d+\.\d+\.\d+\.\d+)",re.M)
            reHostname = re.compile("^Hostname\s*=\s*(.+)",re.M)
            with open(config,'r') as f:
                content = f.read()
            self.server = reServer.findall(content)[0]
            self.host = reHostname.findall(content)[0]
        else:
            self.server = server
            self.host = host

        self.port = port

        # request must be => 'sender data'
        self._packet = {
                'request':'sender data',
                'data':[]
                }

        # get localhost LANG
        self._character = commands.getoutput('echo $LANG').split('.')[-1].upper()


    def packMsg(self,key,value):
        tmp = {
                'host':self.host,
                'key':str(key),
                'value':str(value),
                #'clock':int(datetime.datetime.strftime(datetime.datetime.now(),'%s'))
                'clock':int(time.time())
                }

        self._packet['data'].append(tmp)


    def cleanMsg(self):
        self._packet = {
                'request':'sender data',
                'data':[]
                }


    def formatMsg(self):
        _LANG = 'UTF-8'
        _character = self._character
        if _character == _LANG:
            return json.dumps(self._packet,ensure_ascii = False)
        else:
            return json.dumps(self._packet,ensure_ascii = False).decode(_character).encode(_LANG)

        
    def sendMsg(self):
        if len(self._packet['data']) == 0:
            raise IOError('发送数据前请先打包packMsg(host,key,value)')
        else:
            _packet = self.formatMsg()
            #packlen = len(_packet)
            #_packet = struct.pack("<4sBq" + str(packlen) + "s",'ZBXD',3,packlen,_packet)
            #print _packet

        try:
            sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sk.settimeout(3)
        except Exception,e:
            raise IOError(str(e))

        try:
            sk.connect((self.server,self.port))
            sk.send(_packet)
            #time.sleep(1)
            #print sk.recv(1024)
        except Exception,e:
            raise ValueError(str(e))
        finally:
            sk.close()

