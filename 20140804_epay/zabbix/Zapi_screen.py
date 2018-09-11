#!/usr/bin/env python
# coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import urllib
import urllib2

def execAPI(data):
    # get a json data
    # return a json data
    url = 'http://192.168.11.232/api_jsonrpc.php'
    datas = json.dumps(data)
    req = urllib2.Request(url,datas)
    req.add_header('User-Agent','HTTP/1.1')
    req.add_header('Content-Type','application/json-rpc')
    response = json.loads(urllib2.urlopen(req).read())
    return response

def getAuth():
    login = {
                "jsonrpc":"2.0",
                "method":"user.login",
                "id":0,
                "params":{
                    "user":"Admin",
                    "password":"zabbix"
                }
            }

    response = execAPI(login)
    return response

def getHost(auth,host):
    data = {
                "jsonrpc":"2.0",
                "method":"host.get",
                "id":1,
                "auth":auth,
                "params":{
                    "output":"extend",
                    "filter":{
                        "host":[host]
                    }
                }
            }

    response = execAPI(data)
    return response

def getGraph(auth,hostid):
    data = {
                "jsonrpc":"2.0",
                "method":"graph.get",
                "id":1,
                "auth":auth,
                "params":{
                    "output":"extend",
                    "hostids":hostid
                }
            }

    response = execAPI(data)
    return response

def setScreen(auth,hostname,columns,rows,graphs):
    # ���ж�screen�Ƿ����
    getData = {
                "jsonrpc":"2.0",
                "method":"screen.get",
                "id":1,
                "auth":auth,
                "params":{
                    "output":"extend",
                    "filter":{"name":hostname}
                }
            }

    res = execAPI(getData)["result"]
    if len(res) == 0:
        # ������,����
        setData = {
                    "jsonrpc":"2.0",
                    "method":"screen.create",
                    "id":1,
                    "auth":auth,
                    "params":{
                        "name":hostname,
                        "hsize":columns,
                        "vsize":rows,
                        "private":0,
                        "screenitems":graphs
                    }
                }

    else:
        # ����,����
        setData = {
                    "jsonrpc":"2.0",
                    "method":"screen.update",
                    "id":1,
                    "auth":auth,
                    "params":{
                        "screenid":res[0]["screenid"],
                        "hsize":columns,
                        "vsize":rows,
                        "private":0,
                        "screenitems":graphs
                    }
                }

    # ִ��
    execAPI(setData)


def createScreen(host):
    # ��¼
    auth = getAuth()["result"]
    # ��ȡhostid
    hostinfo = getHost(auth,host)["result"][0]
    hostid = hostinfo["hostid"]
    hostname = hostinfo["name"]
    # ��ȡgraphids
    graphsinfo = getGraph(auth,hostid)["result"]
    # ���graphs
    # �����滮Ϊ3,��������
    total = len(graphsinfo)
    columns = 3
    if total % columns == 0:
        rows = total / columns
    else:
        rows = total / columns + 1

    graphs = []
    x = 0
    y = 0
    for cell in graphsinfo:
        graphTmp = {
                    "resourcetype":0,
                    "resourceid":cell["graphid"],
                    "dynamic":1,
                    "x":x,
                    "y":y
                }
        x += 1
        if x == columns:
            x = 0
            y += 1
        
        graphs.append(graphTmp)

    setScreen(auth,hostname,columns,rows,graphs)

def main():
    with open('netdev.list','r') as f:
        lines = f.readlines()

    for line in lines:
        ip = line.strip('\r\n')
        if ip[:1] == '#':
            pass
        else:
            createScreen(ip)
    

if __name__ == '__main__':
    main()

