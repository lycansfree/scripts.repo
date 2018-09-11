#!/usr/bin/env python
# coding:utf-8

import json
import yaml
import os,sys
import re

import socket
import time
import chardet
#import struct

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

    def packMsg(self,key,value):
        tmp = {
                'host':str(self.host),
                'key':str(key),
                'value':str(value),
                'clock':int(time.time())
                }

        self._packet['data'].append(tmp)

    def cleanMsg(self):
        self._packet = {
                'request':'sender data',
                'data':[]
                }

    def sendMsg(self):
        if len(self._packet['data']) == 0:
            raise IOError('发送数据前请先打包packMsg(host,key,value)')
        else:
            _packet = json.dumps(self._packet)
            _character = chardet.detect(_packet)['encoding']
            _packet = _packet.decode(_character).encode('UTF-8')
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
            #time.sleep(0.5)
            #print sk.recv(1024)
        except Exception,e:
            raise ValueError(str(e))
        finally:
            sk.close()


def check(zbxsender,config,basedir):
    basekey = config["basekey"]
    logseek = os.path.join(basedir,config["logseek"])
    logIDs = config["logIDs"]

    try:
        with open(logseek,'r') as f:
            seekInfo = json.load(f)
    except Exception:
        seekInfo = {}

    for id in logIDs:
        filename = config[id]["logdir"]
        _fileInfo = os.stat(filename)

        jsonID = str(id)
        if jsonID in seekInfo:
            _lastseek,_lastino = seekInfo[jsonID]
            if _lastino == _fileInfo.st_ino and _lastseek <= _fileInfo.st_size:
                # 文件未重新开始轮转且文件未被清空的
                currSeek = _lastseek
            else:
                currSeek = 0
        else:
            currSeek = 0
        
        # 为了一次读取完整,采用_status判断
        _status = False

        recp = re.compile(config[id]["logkey"])
        with open(filename,'r') as f:
            f.seek(currSeek)
            line = f.readline()
            while line:
                if recp.search(line):
                    _status = True

                line = f.readline()
            
            seekInfo[jsonID] = (f.tell(),_fileInfo.st_ino)

        if _status:
            zbxsender.packMsg('%s[%s]' % (basekey,jsonID),'Error Exception')
        else:
            zbxsender.packMsg('%s[%s]' % (basekey,jsonID),'Success')
            

    zbxsender.sendMsg()

    with open(logseek,'w') as f:
        json.dump(seekInfo,f)


def main():
    zbxsender = ZbxSender(config = '/etc/zabbix/zabbix_agentd.conf')

    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    conf = os.path.join(basedir,'zbxLog.yml')
    with open(conf,'r') as f:
        config = yaml.load(f.read().decode('gbk'))

    check(zbxsender,config,basedir)
    zbxsender.cleanMsg()


if __name__ == '__main__':
    main()

