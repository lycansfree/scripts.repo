#!/usr/bin/env python
# coding:utf-8

from mysql import connector
import sys,re

def get_ip_list(dbinfos):
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    _host = '172.16.104.1'
    _port = 6666
    _database = 'migrate'
    allIP = {}
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
        cur = db.cursor()
        cur.execute("select * from ip_check_list")
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

def get_dbinfo():
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    _host = '192.168.80.109'
    _port = 6666
    _database = 'migrate'
    dbinfo = []
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
        cur = db.cursor()
        cur.execute("select * from dbinfo")
        res = cur.fetchall()
        cur.close()
        db.close()
        
        return res

    except Exception,e:
        print str(e)
        sys.exit(2)

def main():
    dbinfos = get_dbinfo()
    get_ip_list(dbinfos)

if __name__ == '__main__':
    main()



