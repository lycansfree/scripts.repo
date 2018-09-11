#!/usr/bin/env python
# coding:utf-8

# 华为云环境用户批量创建

import paramiko
import sys,os
import time
import crypt

# 重写paramiko,获取退出码
class GET_exit_status(paramiko.SSHClient):
    def exec_command(self, command, bufsize=-1):
        """
        为了获取退出码,需要多返回一个chan对象,重写exec_command方法
        """
        chan = self._transport.open_session()
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        return stdin, stdout, stderr, chan

# 创建用户
def add_user(ip,userList):
    _user = ''
    _pwd = ''
    failList = []
    try:
        ssh = GET_exit_status()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,username = _user,password = _pwd)
        for username,password,uid in userList:
            query = 'id %s' % username
            stdin,stdout,stderr,chan = ssh.exec_command(query)
            if int(chan.recv_exit_status()) != 0:
                ppp = crypt.crypt(password,'bjfuzj')
                create = '/usr/sbin/useradd -s /bin/bash -d /home/%s -g develop -u %s -p %s %s\r' % (username,uid,ppp,username)

            time.sleep(0.1)
            # 验证是否创建成功
            stdin,stdout,stderr,chan = ssh.exec_command(query)
            if int(chan.recv_exit_status()) != 0:
                failList.append(username)

        # 判断最终状态
        if len(failList) == 0:
            status = 0
            message = '%s全部创建成功' % ip
        else:
            status = 1
            message = ip + '创建失败的用户列表:' + ','.join(failList)

        ssh.close()

    except Exception,e:
        status = 3
        message = '%s创建异常:%s' % (ip,str(e))

    finally:
        return status,message


def main():
    with open('user.list','r') as f:
        lines = f.readlines()

    allDict = {}
    for line in lines:
        line = line.strip('\n').split()
        ip = line[0]
        username = line[1]
        password = line[2]
        uid = line[3]
        if ip not in allDict:
            allDict[ip] = [(username,password,uid)]
        else:
            allDict[ip].append((username,password,uid))

    for host in allDict:
        add_user(host,allDict[host])


if __name__ == '__main__':
    main()

