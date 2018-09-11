#!/usr/bin/env python
#coding:utf-8

# 发送短信使用

import datetime
import urllib,urllib2

def convert_message(send_string):
    # 获取UTF-16BE编码字符串的byte数组
    array = bytearray(send_string.decode('UTF-8').encode('UTF-16BE'))
    res = ''
    # 将数组成员转换成16进制字符，并去掉0x后组成待发送字符串
    for i in array:
        tmp = hex(i)[2:]
        if len(tmp) < 2:
            tmp = '0' + tmp
        res += tmp
    # 将待发送字符串全部大写，然后返回
    return res.upper()

def main(phone,msgcontent):
    # 空服接口
    URL = 'http://192.168.120.6:9090/ReceiveDataFromBusinessServlet'
    stamptime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    msgcontent = convert_message(msgcontent)
    # 按接口要求填写各参数
    data={
        'msgversion':1,
        'msgtype':1,
        'sequencenumber':stamptime,
        'sendingtype':2,
        'msisdn':phone,
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
    # 打开request，发送
    response = urllib2.urlopen(req)
    # 获取response并读取，打印
    res = response.read()
    #print res

if __name__ == '__main__':
    main(phone,msgcontent)
    
