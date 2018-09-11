#!/usr/bin/env python
# coding:utf-8

from mysql import connector
import sys,os
import xlrd

def set_dbinfo(insertList):
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    _host = '192.168.80.109'
    _port = 6666
    _database = 'migrate'
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
        cur = db.cursor()
        cur.executemany("insert into deploy_info (username,platform,appdir,bindir,port,startshell,stopshell,uri,bakcomm) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",insertList)
        db.commit()
        cur.close()
        db.close()

    except Exception,e:
        print str(e)
        sys.exit(2)


def main():
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    #filename = os.path.join(basedir,'dbinfo.txt')
    #with open(filename,'r') as f:
    #    lines = f.readlines()

    filename = os.path.join(basedir,'newPY.xlsx')
    insertList = []
    s = xlrd.open_workbook(filename)
    t = s.sheets()[0]
    for i in range(t.nrows):
        #Fdir,Fname = os.path.split(t.row(i)[5].value)
        insertList.append((t.row(i)[0].value,t.row(i)[1].value,t.row(i)[2].value,t.row(i)[3].value,t.row(i)[4].value,t.row(i)[5].value,t.row(i)[6].value,t.row(i)[7].value,t.row(i)[8].value))

    set_dbinfo(insertList)

            
if __name__ == '__main__':
    main()

