#!/usr/bin/env python
# coding:utf-8

from jenkins import Jenkins
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')


def main():
    jks = Jenkins('http://172.16.73.10:8080/jenkins',username = 'admin',password = 'ZL.pay@2015')
    allJobs = jks.get_all_jobs()
    for line in allJobs:
        preName = line['fullname']
        if preName != 'template':
            jks.delete_job(preName.encode('utf-8'))

if __name__ == '__main__':
    main()

