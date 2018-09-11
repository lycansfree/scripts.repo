# coding:utf-8

from mysql import connector
from jenkins import Jenkins
import sys,os


def get_conn():
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    #_host = '172.16.104.1'
    _host = '192.168.80.109'
    _port = 6666
    _database = 'migrate'
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
        status = True
    except Exception,e:
        status = False
        db = str(e)
    finally:
        return status,db

def get_dbinfo(db):
    try:
        cur = db.cursor()
        cur.execute("select name from jenkins")
        res = cur.fetchall()
        existList = []
        for name, in res:
            existList.append(name)
        status = True
    except Exception,e:
        status = False
        existList = str(e)
    finally:
        cur.close()
        return status,existList

def set_dbinfo(db,insertList):
    try:
        cur = db.cursor()
        cur.executemany("insert into jenkins values (%s,%s)",insertList)
        db.commit()
        print "insert success"
    except Exception,e:
        print str(e)

def main():
    status,db = get_conn()
    if not status:
        print db
        sys.exit(2)

    status,existList = get_dbinfo(db)
    if not status:
        print existList
        sys.exit(2)

    try:
        #jks = Jenkins('http://172.16.73.10:8080/jenkins',username = 'admin',password = 'ZL.pay@2015')
        jks = Jenkins('http://192.168.11.72:8080/jenkins',username = 'admin',password = 'ZL.pay@2015')
        allJobs = jks.get_all_jobs()
        insertList = []
        for line in allJobs:
            preName = line['fullname']
            if preName not in existList:
                insertList.append((preName,0))
                # insertList.append(preName)
    except Exception,e:
        print str(e)
        sys.exit(2)

    # print '\n'.join(insertList)
    set_dbinfo(db,insertList)
    db.close()

if __name__ == '__main__':
    main()



