#!/usr/bin/env python
# coding:utf-8

from mysql import connector
from jenkins import Jenkins
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')


def get_dbinfo():
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    #_host = '172.16.104.1'
    _host = '192.168.80.109'
    _port = 6666
    _database = 'migrate'
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
        cur = db.cursor()
        cur.execute("select * from jenkins where seqs = 1")
        res = cur.fetchall()
        cur.close()
        db.close()
        return res

    except Exception,e:
        print str(e)
        sys.exit(2)

def main():
    res = get_dbinfo()
    #jks = Jenkins('http://172.16.73.10:8080/jenkins',username = 'admin',password = 'ZL.pay@2015')
    jks = Jenkins('http://192.168.11.72:8080/jenkins',username = 'admin',password = 'ZL.pay@2015')
    for name,seqs in res:
        try:
            jks.build_job(name.encode('utf-8'),parameters={'main':'stop'})
        except Exception,e:
            print "%s - %s" % (name.encode('gbk'),str(e))

if __name__ == '__main__':
    main()

