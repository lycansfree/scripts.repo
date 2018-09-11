#!/usr/bin/env python
# coding:utf-8

'''zabbix推送安装脚本'''

import paramiko
import sys,os
import time

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


# 单纯负责上传
def upload(ip,username,passwd,localdir,remotedir,filename,port=22):
    try:
        t = paramiko.Transport((ip,port))
        t.connect(username=username,password=passwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        for file in filename:
            sftp.put(os.path.join(localdir,file),os.path.join(remotedir,file))

        print "传输完成"
        sftp.close()
        t.close()

    except Exception,e:
        print ip + '传输失败:' + str(e)
        sys.exit(3)


# 传输安装脚本
def put_install(ip,username,passwd,localdir,remotedir,filename):
    try:
        ssh = GET_exit_status()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,username=username,password=passwd)
        cmd = 'ls ' + remotedir
        stdin,stdout,stderr,chan = ssh.exec_command(cmd)

        # 需要上传file_temp中文件
        tran_flag = 0
        if int(chan.recv_exit_status()) == 0:
            file_list = stdout.read().strip().split('\n')
            # 取差集，filename中有而file_list中没有的
            file_temp = list(set(filename).difference(set(file_list)))
            if len(file_temp) == 0:
                # 全部上传成功
                tran_flag = 1
        else:
            # 文件夹不存在,需要创建
            cmd = 'mkdir -p ' + remotedir
            stdin,stdout,stderr,chan = ssh.exec_command(cmd)
            if int(chan.recv_exit_status()) == 0:
                print remotedir + "创建成功"
                file_temp = filename
            else:
                print ip + ' ' + remotedir + "创建失败"
                sys.exit(2)

        ssh.close()

    except Exception,e:
        print ip + "连接失败:" + str(e)
        sys.exit(3)

    if tran_flag == 0:
        # 临时增加,之后改install脚本
        file_temp = filename
        print "开始上传:" + str(file_temp)
        upload(ip,username,passwd,localdir,remotedir,file_temp)
    else:
        print "无需上传"


# 执行安装
def exec_install(ip,username,passwd,remotedir):
    query = 'ls /etc/rc.d/init.d/zabbix-agent'
    try:
        ssh = GET_exit_status()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,username=username,password=passwd)
        stdin,stdout,stderr,chan = ssh.exec_command(query)
        if int(chan.recv_exit_status()) == 0:
            print 'zabbix已经安装'
        else:
            create = 'sudo sh %s' % os.path.join(remotedir,'install_zabbix.sh')
            stdin,stdout,stderr,chan = ssh.exec_command(create)
            if int(chan.recv_exit_status()) == 0:
                print 'zabbix安装完成'
            else:
                print 'zabbix安装失败,%s' % stdout.read()
                sys.exit(2)
            
        ssh.close()

    except Exception,e:
        print ip + "执行异常:" + str(e)
        sys.exit(3)



def main():
    try:
        ip = sys.argv[1]
    except Exception,e:
        print str(e)
        sys.exit(1)
    username = 'suweihu'
    passwd = '-wIO19ezj'

    localdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    remotedir = '/home/suweihu/zabbix'
    filename = ['zabbix-agent-3.2.1-1.el6.x86_64.rpm','install_zabbix.sh']
    # 传输并执行
    put_install(ip,username,passwd,localdir,remotedir,filename)
    exec_install(ip,username,passwd,remotedir)


if __name__ == '__main__':
    main()

