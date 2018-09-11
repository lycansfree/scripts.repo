#!/usr/bin/env python
# coding:utf-8

from jenkins import Jenkins
from mysql import connector
import sys,re

def get_ip_list():
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
        cur.close()
        db.close()

        return allIP

    except Exception,e:
        print str(e)
        sys.exit(2)


def main():
    allIP = get_ip_list()
    s = Jenkins('http://192.168.11.72:8080/jenkins',username = 'admin',password = 'ZL.pay@2015')
    bs = Jenkins('http://172.16.73.10:8080/jenkins',username = 'admin',password = 'ZL.pay@2015')
    allJobs = s.get_all_jobs()
    #allJobs = bs.get_all_jobs()
    recp = re.compile("(192.168.\d+\.\d+)")
    for line in allJobs:
        preName = line['fullname']
        name = preName.encode('utf-8')
        ipFIND = recp.findall(preName)
        if len(ipFIND) > 0:
            ip = ipFIND[0]
            createXML = s.get_job_config(name)
            try:
                succName = preName.replace(ip,allIP[ip]).encode('utf-8')
                createXML = createXML.replace(ip,allIP[ip])
            except Exception,e:
                print str(e)
                continue
            try:
                bs.create_job(succName,createXML)
            except Exception,e:
                print preName
            

        #bs.delete_job(name)
        #createXML = createXML.replace('192.168.31.13','172.16.74.5')
        ##print createXML
        #bs.create_job(name.replace('192.168.31.13','172.16.74.5'),createXML)
        ##bs.reconfig_job(line['fullname'].encode('utf-8'),createXML)
        #break

    #createXML = s.get_job_config(name)
    #bs.create_job(name,createXML)
    #print bs.get_job_name(name.decode('gbk').encode('utf-8'))
    

if __name__ == '__main__':
    main()

