#!/usr/bin/env python
# coding:utf-8

from mysql import connector
import sys,os
import paramiko

class GET_exit_status(paramiko.SSHClient):
    def exec_command(self, command, timeout = None, bufsize=-1):
        """
        重写exec_command方法,获取退出码,增加超时
        """
        chan = self._transport.open_session()
        if timeout is not None:
            chan.settimeout(timeout)
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        # 在这里用recv_exit_status方法,会阻塞直到获取结果,导致timeout不可用
        # stdstatus = int(chan.recv_exit_status())
        return stdin, stdout, stderr, chan

def get_dbinfo():
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    _host = '192.168.80.109'
    _port = 6666
    _database = 'migrate'
    allFile = []
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
        cur = db.cursor()
        cur.execute("select ip,filedir,filename from dbinfo")
        for ip,filedir,filename in cur.fetchall():
            allFile.append((ip,os.path.join(filedir,filename)))

        cur.close()
        db.close()

        return allFile

    except Exception,e:
        print str(e)
        sys.exit(2)

def check(ip,filename):
    username = 'suweihu'
    password = '-wIO19ezj'
    try:
        ssh = GET_exit_status()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,username=username,password=password)
        stdin,stdout,stderr,chan = ssh.exec_command('sudo ls %s' % filename)
        if int(chan.recv_exit_status()) > 0:
            raise ValueError('无此文件')

        ssh.close()

    except Exception,e:
        print ip


def main():
    allFile = get_dbinfo()
    for ip,filename in allFile:
        check(ip,filename)

            
if __name__ == '__main__':
    main()

