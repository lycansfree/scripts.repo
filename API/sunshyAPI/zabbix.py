
import json
import urllib
import urllib2
import socket
import time
import re
import os


# zabbix rpc interface
class Zabbix(object):
    def __init__(self, username = '',password = '', host = '', port = 8000):
        self.url = 'http://%s:%d/zabbix/api_jsonrpc.php' % (host, port)
        data = {
            "jsonrpc":"2.0",
            "method":"user.login",
            "id":0,
            "params":{
                "user":username,
                "password":password
            }
        }
         
        req = urllib2.Request(self.url, json.dumps(data))
        req.add_header('User-Agent','HTTP/1.1')
        req.add_header('Content-Type','application/json-rpc')
        self.auth = json.loads(urllib2.urlopen(req).read())['result']
 
 
    def execAPI(self,method,param):
        data = {
            "jsonrpc":"2.0",
            "method":method,
            "id":1,
            "auth":self.auth,
            "params":param
        }
 
        req = urllib2.Request(self.url, json.dumps(data))
        req.add_header('User-Agent','HTTP/1.1')
        req.add_header('Content-Type','application/json-rpc')
        response = json.loads(urllib2.urlopen(req).read())
        return response['result']
 

# zabbix sender by python
class ZbxSender(object):
    def __init__(self,server = '127.0.0.1', host = '127.0.0.1', port = 10051, config = None):
        if config is not None:
            self.server = self.host = None
            recp = re.compile("^(?<!#)\s*(\w+)\s*=\s*(.+)",re.M)
            with open(config,'r') as f:
                content = f.read()
            reConf = recp.findall(content)
            for zbx_conf_name,zbx_conf_value in reConf:
                if zbx_conf_name == 'Server':
                    self.server = zbx_conf_value.split(',')[0]
                elif zbx_conf_name == 'Hostname':
                    self.host = zbx_conf_value.split(',')[0]
             
            if self.server is None:
                raise ValueError('zabbix_server配置异常')
 
            if self.host is None:
                self.host = socket.gethostname()
 
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
        _lang = os.getenv('LANG')
        if _lang is None:
            raise ValueError('语言编码$LANG获取失败')
        else:
            self._character = _lang.split('.')[-1].upper()
         
 
    def packMsg(self,key,value):
        tmp = {
                'host':self.host,
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
 
        try:
            sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sk.settimeout(3)
        except Exception as e:
            raise IOError(str(e))
 
        try:
            sk.connect((self.server,self.port))
            sk.send(_packet)
            # time.sleep(1)
            # print sk.recv(1024)
        except Exception as e:
            raise ValueError(str(e))
        finally:
            sk.close()
 
