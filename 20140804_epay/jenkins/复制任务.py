#!/usr/bin/env python
# coding:utf-8

from jenkins import Jenkins
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')



def main():
    ooojks = Jenkins('http://192.168.11.211:8080/jenkins',username = 'admin',password = 'ZL.pay@2015')
    jks = Jenkins('http://192.168.11.72:8080/jenkins',username = 'admin',password = 'ZL.pay@2015')
    allJobs = ooojks.get_all_jobs()
    for line in allJobs:
        preName = line['fullname']
        switchName = line['fullname'].encode('utf-8')
        try:
            jks.copy_job('template',switchName)
        except Exception,e:
            print preName

if __name__ == '__main__':
    main()

