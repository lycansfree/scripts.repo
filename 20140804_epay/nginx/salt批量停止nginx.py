#!/usr/bin/env python
# coding:utf-8

from mysql import connector
import sys,re

def nginxinfo():
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    _host = '192.168.80.109'
    _port = 6666
    _database = 'migrate'
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
    except Exception,e:
        print "connect exception:%s" % str(e)
        return False

    try:
        cur = db.cursor()
        cur.execute("select * from nginxinfo")
        res = cur.fetchall()
        for oldip,newip in res:
            allIP[oldip] = newip


        insList = []
        for id,ip,dbname,operate,lastoperate,lastoutput,lasttime,bakcomm,filedir,filename,pfile in dbinfos:
            try:
                insList.append((id,allIP[ip],dbname,operate,lastoperate,lastoutput,lasttime,bakcomm,filedir,filename,pfile))
            except Exception,e:
                print "%d - %s" % (id,ip)

        cur.executemany("insert into dbinfo values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",insList)
        db.commit()

        cur.close()
        db.close()

    except Exception,e:
        print str(e)
        sys.exit(2)

