#!/usr/bin/env python
# encoding:utf-8

import smtplib
from email.mime.text import MIMEText


def sendmail(contact_list,subject,message):
    HOST = '127.0.0.1'
    USER = 'nagios'
    #suffix = 'chinaunicom.cn'
    suffix = 'wo.com.cn'

    myself = '联通支付-技术部'+'<'+USER+'@'+suffix+'>'
    msg = MIMEText(message,_subtype='html',_charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = myself
    msg['To'] = ';'.join(contact_list)
    try:
        server = smtplib.SMTP()
        server.connect(HOST)
        # server.login(USER,PASSWORD)
        server.sendmail(myself,contact_list,msg.as_string())
    except Exception,e:
        pass
    finally:
        server.close()


def main():
    pass


if __name__ == '__main__':
    main()
    
