#!/usr/bin/env python
#coding:utf-8

import urllib2
import json
import sys
import urllib

def GetToken():
    token_data = {}
    token_data['corpid'] = 'ww256dd74ae71d69c4'
    token_data['corpsecret'] = 'bN6QR3rVHsfDRa6dKYYF1jnL0GXvGbt07E9nFbNrRH8'
    token_host = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    token_msg = urllib.urlencode(token_data)

    # POST方式,20161018发现微信开始不支持post了,改成GET
    # req = urllib2.Request(token_host,token_msg)
    # GET方式
    req = urllib2.Request(token_host + '?' + token_msg)
    response = urllib2.urlopen(req)
    res = response.read()
    token_key = json.loads(res)["access_token"]
    return token_key

def SendMsg(Msg_url,contact,message):
    data = {}
    data['touser'] = contact
    data['msgtype'] = 'text'
    data['agentid'] = 1000002
    data['text'] = {'content':message}
    Msg = json.dumps(data,ensure_ascii=False)
    req = urllib2.Request(Msg_url,Msg)
    ResP = urllib2.urlopen(req).read()
    JResP = json.loads(ResP)
    errcode = JResP["errcode"]
    errmsg = JResP["errmsg"]
    if errcode != 0:
        raise IOError(errmsg)

def qywx(contact,subject,message):
    try:
        # 获取token值
        # PS:微信官方token值超时为7200秒
        token_key = GetToken()
        Msg_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + token_key
        # 发送
        SendMsg(Msg_url,contact,message)

    except Exception,e:
        # 微信发送失败,短信通知管理员
        import sunshy_sms
        sunshy_sms.main('18500948348','nagios企业微信异常:' + str(e))

def main():
    try:
        contact = sys.argv[1]
        subject = sys.argv[2]
        message = sys.argv[3]
        qywx(contact,subject,message)

    except Exception,e:
        print str(e)

if __name__ == '__main__':
    main()

