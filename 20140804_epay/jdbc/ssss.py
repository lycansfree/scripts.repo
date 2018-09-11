#!/usr/bin/env python
# coding:utf-8

from mysql import connector
import sys,os

def get_dbinfo():
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    _host = '172.16.104.1'
    _port = 6666
    _database = 'migrate'
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
        cur = db.cursor()
        cur.execute("select dictvalue from contrast_info where dictname = 'HOSTINFO'")
        res = cur.fetchall()
        cur.close()
        db.close()
        return res

    except Exception,e:
        print str(e)
        sys.exit(2)

def main():
    res = get_dbinfo()
    for ipList, in res:
        ips = ipList.split('|')
        for ip in ips:
            with open('duizhao.sql','a') as f:
                f.write("insert into contrast_info (dictname, dictkey, dictvalue) values ('HOSTON','%s','');\n" % ip)

if __name__ == '__main__':
    main()

