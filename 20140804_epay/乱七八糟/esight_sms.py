#!/usr/bin/env python
# coding:utf-8

import urllib,urllib2
import datetime
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
import chardet


class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        postdata = self.rfile.read(int(self.headers['content-length']))
        kvdata = urllib2.parse_keqv_list(postdata.split('&'))
        try:
            if kvdata['messagetype'] == 'test':
                _status_ = 200
                _response_ = 'success'
            elif kvdata['messagetype'] == 'send':
                _response_,_status_ = sendSMS(kvdata['mobile'],'esight warning:' + kvdata['message'])
            else:
                raise ValueError('messagetype=[test|send]')
        except Exception,e:
            _status_ = 400
            _response_ = str(e)
        finally:
            self.send_response(_status_,_response_)
                
    def do_GET(self):
        uri = urllib.splitquery(self.raw_requestline.split()[1])[1]
        print urllib.unquote(uri)
        print uri
        kvdata = urllib2.parse_keqv_list(urllib.unquote(uri).split('&'))
        # print kvdata
        try:
            if kvdata['messagetype'] == 'test':
                _status_ = 200
                _response_ = 'success'
            elif kvdata['messagetype'] == 'send':
                for _mobile in kvdata['mobile'].split(','):
                    _response_,_status_ = sendSMS(_mobile,'esight warning:' + kvdata['message'])
            else:
                raise ValueError('messagetype=[test|send]')
        except Exception,e:
            _status_ = 400
            _response_ = str(e)
        finally:
            self.send_response(_status_,_response_)
                
    
def formatSMS(message):
    #_character = chardet.detect(message)['encoding']
    _character = 'GBK'
    # 获取UTF-16BE编码字符串的byte数组
    array = bytearray(message.decode(_character).encode('UTF-16BE'))
    res = ''
    # 将数组成员转换成16进制字符，并去掉0x后组成待发送字符串
    for i in array:
        tmp = hex(i)[2:]
        if len(tmp) < 2:
            tmp = '0' + tmp
        res += tmp
    # 将待发送字符串全部大写，然后返回
    return res.upper()

def sendSMS(_mobilephone,_message):
    URL = 'http://192.168.120.6:9090/ReceiveDataFromBusinessServlet'
    stamptime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    msgcontent = formatSMS(_message)
    # 按接口要求填写各参数
    data = {
        'msgversion':1,
        'msgtype':1,
        'sequencenumber':stamptime,
        'sendingtype':2,
        'msisdn':_mobilephone,
        'clientid':'jkpt',
        'smsgatewaya1':'1018810010',
        'smsgatewaya2':'',
        'keepsession':0,
        'bizcode':'11002',
        'reportflag':1,
        'stamptime':stamptime,
        'msgcmd':'11',
        'msgencode':8,
        'msgcontent':msgcontent,
        'taskmsisdnflag':0,
        'taskid':0,
        'expiretime':'',
        'scheduletime':'',
        'iccid':'',
        'appid':'',
        'mac':''
    }
    # 将data从dict转换为待发送字符串格式：a=a1&b=b1
    message = urllib.urlencode(data)
    # 获取request变量
    req = urllib2.Request(URL,message)
    # 访问目标
    try:
        _response = urllib2.urlopen(req)
        _status = 200
    except Exception,e:
        _response = str(e)
        _status = 500
    finally:
        return _response,_status

def main():
    httpd = HTTPServer(('192.168.116.1',6666),MyHTTPHandler)
    httpd.request_queue_size = 0
    httpd.allow_reuse_address = True
    httpd.serve_forever()

if __name__ == '__main__':
    main()

