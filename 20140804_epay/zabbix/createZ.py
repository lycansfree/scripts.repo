#!/usr/bin/env python
# coding:utf-8

'''zabbix���Ͱ�װ�ű�'''

import paramiko
import sys,os
import time

# ��дparamiko,��ȡ�˳���
class GET_exit_status(paramiko.SSHClient):
    def exec_command(self, command, bufsize=-1):
        """
        Ϊ�˻�ȡ�˳���,��Ҫ�෵��һ��chan����,��дexec_command����
        """
        chan = self._transport.open_session()
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        return stdin, stdout, stderr, chan


# ���������ϴ�
def upload(ip,username,passwd,localdir,remotedir,filename,port=22):
    try:
        t = paramiko.Transport((ip,port))
        t.connect(username=username,password=passwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        for file in filename:
            sftp.put(os.path.join(localdir,file),os.path.join(remotedir,file))

        print "�������"
        sftp.close()
        t.close()

    except Exception,e:
        print ip + '����ʧ��:' + str(e)
        sys.exit(3)


# ���䰲װ�ű�
def put_install(ip,username,passwd,localdir,remotedir,filename):
    try:
        ssh = GET_exit_status()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,username=username,password=passwd)
        cmd = 'ls ' + remotedir
        stdin,stdout,stderr,chan = ssh.exec_command(cmd)

        # ��Ҫ�ϴ�file_temp���ļ�
        tran_flag = 0
        if int(chan.recv_exit_status()) == 0:
            file_list = stdout.read().strip().split('\n')
            # ȡ���filename���ж�file_list��û�е�
            file_temp = list(set(filename).difference(set(file_list)))
            if len(file_temp) == 0:
                # ȫ���ϴ��ɹ�
                tran_flag = 1
        else:
            # �ļ��в�����,��Ҫ����
            cmd = 'mkdir -p ' + remotedir
            stdin,stdout,stderr,chan = ssh.exec_command(cmd)
            if int(chan.recv_exit_status()) == 0:
                print remotedir + "�����ɹ�"
                file_temp = filename
            else:
                print ip + ' ' + remotedir + "����ʧ��"
                sys.exit(2)

        ssh.close()

    except Exception,e:
        print ip + "����ʧ��:" + str(e)
        sys.exit(3)

    if tran_flag == 0:
        # ��ʱ����,֮���install�ű�
        file_temp = filename
        print "��ʼ�ϴ�:" + str(file_temp)
        upload(ip,username,passwd,localdir,remotedir,file_temp)
    else:
        print "�����ϴ�"


# ִ�а�װ
def exec_install(ip,username,passwd,remotedir):
    query = 'ls /etc/rc.d/init.d/zabbix-agent'
    try:
        ssh = GET_exit_status()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,username=username,password=passwd)
        stdin,stdout,stderr,chan = ssh.exec_command(query)
        if int(chan.recv_exit_status()) == 0:
            print 'zabbix�Ѿ���װ'
        else:
            create = 'sudo sh %s' % os.path.join(remotedir,'install_zabbix.sh')
            stdin,stdout,stderr,chan = ssh.exec_command(create)
            if int(chan.recv_exit_status()) == 0:
                print 'zabbix��װ���'
            else:
                print 'zabbix��װʧ��,%s' % stdout.read()
                sys.exit(2)
            
        ssh.close()

    except Exception,e:
        print ip + "ִ���쳣:" + str(e)
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
    # ���䲢ִ��
    put_install(ip,username,passwd,localdir,remotedir,filename)
    exec_install(ip,username,passwd,remotedir)


if __name__ == '__main__':
    main()

