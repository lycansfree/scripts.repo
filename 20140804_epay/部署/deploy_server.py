#!/usr/bin/env python
# coding:utf-8

import paramiko
import sys,os
from mysql import connector
import getopt
from ftplib import FTP
import yaml

class GET_exit_status(paramiko.SSHClient):
    def exec_command(self, command, timeout = None, bufsize=-1):
        """
        ��дexec_command����,��ȡ�˳���,���ӳ�ʱ
        """
        chan = self._transport.open_session()
        if timeout is not None:
            chan.settimeout(timeout)
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        # ��������recv_exit_status����,������ֱ����ȡ���,����timeout������
        # stdstatus = int(chan.recv_exit_status())
        return stdin, stdout, stderr, chan

def configparser(filename):
    import zipfile
    config = {}
    name = 'others'
    if zipfile.is_zipfile(filename):
        zipreader = zipfile.ZipFile(filename,'r')
        pfile = os.path.basename(filename)[:-4] + '.lst'
        # content = zipreader.read(pfile)
        content = zipreader.open(pfile).readlines()
       # _list = zipreader.namelist()
       # filelist = []
       # for i in _list:
       #     if i[-1] == '/':
       #         pass
       #     else:
       #         filelist.append(i)
        zipreader.close()
        # ÿ����Ҫ��ӡ��lst�ļ�����
        print content

        # for line in content.split('\n'):
        for line in content:
            line = line.strip('\r\n ')
            if len(line) > 0:
                if line[0] == '[':
                    name = line.strip('[]')
                    continue
                elif line[0] == '#':
                    pass
                else:
                    if name in ('START_SERVICES','START_SERVICES_GROUPS','SERVICE_ALL','JBOSS'):
                        if name not in config:
                            config[name] = {}
                        line = line.split('=')
                        config[name][line[0].strip()] = line[1].strip()

        return config
    else:
        raise ValueError("ICSƽ̨��Ҫʹ��zip��ʽ�鵵�ļ�")


def checkhips(services,hipsInfo):
    import re
    refind = re.compile("^([a-zA-Z].+?)\s+.+?\s+(.+?)\s+",re.M)
    ships = []
    ghips = []
    for s,g in refind.findall(hipsInfo):
        ships.append(s)
        ghips.append(g)

    errorhips = []
    for service in services.split(','):
        if service not in ships and service not in ghips:
            errorhips.append(service)

    return errorhips


def exec_deploy(_id,mainType,dbinfo,target,filenames,_version,localdir):
    status = 2
    try:
        ssh = GET_exit_status()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(target,username = 'suweihu',password = '-wIO19ezj')
        sftp = ssh.open_sftp()
    except Exception,e:
        print "���������쳣:%s" % str(e)
        return status

    try:
        tmpdir = '/app/jenkinsTMP/' + _id
        _client = tmpdir + '/deploy_client.sh'
        stdin,stdout,stderr,chan = ssh.exec_command('mkdir -p %s' % tmpdir)
        if int(chan.recv_exit_status()) > 0:
            raise IOError('����%sʧ��' % tmpdir)
        
        stdin,stdout,stderr,chan = ssh.exec_command("sudo su - %s -c 'echo $LANG' | grep -i utf" % dbinfo['username'])
        if int(chan.recv_exit_status()) == 0:
            # UTF-8
            _character = 'UTF-8'
            sftp.put('/app/wzf/pydeploy/script/wzf_utf8.sh',_client)
        else:
            # GBK
            _character = 'GB18030'
            sftp.put('/app/wzf/pydeploy/script/wzf_gbk.sh',_client)

        # ��ȡuser��Ŀ¼
        stdin,stdout,stderr,chan = ssh.exec_command(''' cat /etc/passwd | awk -F ":" '{if($1 == "%s") print $6}' ''' % dbinfo['username'])
        u_client = os.path.join(stdout.read().strip('\n\r'),'autodeploy/deploy_client.sh')
        # cp��chown
        stdin,stdout,sterr,chan = ssh.exec_command('sudo mkdir -p %s;sudo cp %s %s' % (os.path.dirname(u_client),_client,u_client))
        if int(chan.recv_exit_status()) > 0:
            raise IOError('����%sʧ��' % u_client)
        
        stdin,stdout,sterr,chan = ssh.exec_command('sudo chown -R %s:develop %s' % (dbinfo['username'],os.path.dirname(u_client)))
        if int(chan.recv_exit_status()) > 0:
            raise IOError('��Ȩ%sʧ��' % u_client)

        # deployģʽʱ�ϴ������
        if mainType == 'deploy':
            for filename in filenames.split(','):
                sftp.put(os.path.join(localdir,filename),os.path.join(tmpdir,filename))

        # ִ�в���ű�
        if len(dbinfo['uri']) == 0:
            url = ''
        else:
            url = 'http://%s:%s/%s' % (target,dbinfo['port'],dbinfo['uri'])

        if dbinfo['platform'] == 'ics':
            # ICSƽ̨�ȶ�ȡ��ͣ����
            # ��У�����������ѡ���Ƿ���ȷ
            ics_config = configparser(filenames)
            if len(ics_config) == 0:
                raise ValueError('δ���ո�ʽ��д��������')
            
            for ics_type in ics_config:
                if ics_type in ('START_SERVICES','START_SERVICES_GROUPS'):
                    for ics_name in ics_config[ics_type]:
                        # ����ǰ�Ȼ�ȡ�������б�����б�
                        stdin,stdout,stderr,chan = ssh.exec_command("sudo su - %s -c 'hips -a'" % ics_name)
                        _Ehips = checkhips(ics_config[ics_type][ics_name],stdout.read())
                        if len(_Ehips) > 0:
                            raise ValueError('%s�û���������д����:%s' % (ics_name,','.join(_Ehips)))


        # ִ��client�ű�
        stdin,stdout,stderr,chan = ssh.exec_command(''' sudo su - %s -c "bash --login %s -plf %s -app %s -tmp %s -bin %s -port %s -url %s -version %s -file %s -start '%s' -stop '%s' -main %s -exit" ''' % (dbinfo['username'],u_client,dbinfo['platform'],dbinfo['appdir'],tmpdir,dbinfo['bindir'],dbinfo['port'],url,_version,filenames,dbinfo['startshell'],dbinfo['stopshell'],mainType))

        while True:
            try:
                # ����ʵʱ��ӡ
                sys.stdout.flush()
                # ��ʽ��client�˽ű�ִ�����
                print stdout.next().strip('\n\r').decode(_character).encode('GB18030')
            except Exception:
                print "ִ�����"
                break

        status = int(chan.recv_exit_status())
        if status > 0:
            raise IOError('����ϸ���')

        if dbinfo['platform'] == 'ics':
            # ICSʹ��paramiko����hiboot/hips
            bootUser = []
            for ics_type in ics_config:
                for ics_name in ics_config[ics_type]:
                    if ics_type == 'START_SERVICES':
                        # hiboot -s
                        for ics_service in ics_config[ics_type][ics_name].split(','):
                            stdin,stdout,stderr,chan = ssh.exec_command("sudo su - %s -c 'hiboot -s %s'" % (ics_name,ics_service))
                            print stdout.read()
                            sys.stdout.flush()
                    elif ics_type == 'START_SERVICES_GROUPS':
                        # hiboot -g
                        for ics_service in ics_config[ics_type][ics_name].split(','):
                            stdin,stdout,stderr,chan = ssh.exec_command("sudo su - %s -c 'hiboot -g %s'" % (ics_name,ics_service))
                            print stdout.read()
                            sys.stdout.flush()
                    elif ics_type == 'SERVICE_ALL':
                        # hiboot -a
                        if ics_config[ics_type][ics_name] == 'all':
                            stdin,stdout,stderr,chan = ssh.exec_command("sudo su - %s -c 'hiboot -a'" % (ics_name))
                            print stdout.read()
                            sys.stdout.flush()
                    elif ics_type == 'JBOSS':
                        # jboss
                        if ics_config[ics_type][ics_name] == 'yes':
                            stdin,stdout,stderr,chan = ssh.exec_command("sudo su - %s -c 'cd ~/jboss5/bin;sh start.sh 1>/dev/null 2>&1;hiboot -a'" % (ics_name))
                            print stdout.read()
                            sys.stdout.flush()
                    else:
                        raise ValueError('δ֪ICSƽ̨��������')

                    bootUser.append(ics_name)

            bootUser = list(set(bootUser))
            for ics_name in bootUser:
                stdin,stdout,stderr,chan = ssh.exec_command("sudo su - %s -c 'hips -a'" % (ics_name))
                # СBUG,���ø���,ʵ��Ӧȡ���ر���,���Ƚ��ж��Ƿ�ת��,��Ӧ��д��
                # print stdout.read().decode(_character).encode('GB18030')
                print stdout.read()
                sys.stdout.flush()
            
            
    except Exception,e:
        print "ִ���쳣:%s" % str(e)
        status = 3
    
    finally:
        sftp.close()
        ssh.close()
        return status
        

def getConf(_id):
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    _host = '192.168.80.109'
    _port = 6666
    _database = 'migrate'
    _flag = True
    dbinfo = {}

    # ��������
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
    except Exception,e:
        dbinfo = str(e)
        return False,dbinfo

    try:
        cur = db.cursor()
        cur.execute("select * from deploy_info where id = %d" % (int(_id)))
        res = cur.fetchall()
        dbinfo['username'] = res[0][1]
        dbinfo['platform'] = res[0][2]
        dbinfo['appdir'] = res[0][3]
        dbinfo['bindir'] = res[0][4]
        dbinfo['port'] = res[0][5]
        dbinfo['startshell'] = res[0][6]
        dbinfo['stopshell'] = res[0][7]
        dbinfo['uri'] = res[0][8]

    except Exception,e:
        dbinfo = str(e)
        _flag = False

    finally:
        # �ر�����
        cur.close()
        db.close()
        return _flag,dbinfo


def getFiles(filenames,localdir,ftpdir = '/autodeploy'):
    ip = '192.168.7.244'
    username = 'unicompay1'
    passwd = 'unicompay1'
    filenames = filenames.split(',')

    try:
        # �л�������·��
        os.chdir(localdir)

        # ��¼ftp
        ftp = FTP(ip)
        ftp.login(username,passwd)
        ftp.cwd(ftpdir)
        # �г�ftp�ϵ��ļ�
        flf = ftp.nlst()
        status = 0
        for filename in filenames:
            if filename not in flf:
                print filename + '������,�޷�����'
                status += 1

        if status > 0:
            sys.exit(2)

        fileSize = {}
        for filename in filenames:
            fileSize[filename] = ftp.size(filename)
            with open(filename,'wb') as f:
                ftp.retrbinary('RETR' + filename,f.write,4096)

        ftp.close()

        # ������ɺ�У���С
        for filename in fileSize:
            if fileSize[filename] != os.path.getsize(filename):
                print filename + "�ļ���СУ��ʧ��"
                status += 1
            else:
                print filename + '��С:' + str(fileSize[filename])

        if status == 0:
            print "�ļ�ȫ�����سɹ�"
        else:
            sys.exit(2)

    except Exception,e:
        print "FTP���ӳ����쳣:" + str(e)
        sys.exit(3)



def print_help(message = None):
    if message is None:
        print "Usage:python %s --id=id --file=filename --main=mainType --target=192.168.0.0/16 --version=version --ftpdir=ftpdir" % sys.argv[0]
    else:
        print message
    sys.exit(2)


def checkIP(ip):
    host = ip.split('.')
    if len(host) != 4:
        return False
    else:
        if host[0] == '192' and host[1] == '168' and int(host[2]) < 255 and int(host[3]) < 255:
            return True
        else:
            return False
    

def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],"h",["id=","file=","main=","target=","version=","ftpdir="])
        if len(args) > 0:
            raise ValueError("%s is unknown arguement" % '|'.join(args))
    except Exception,e:
        print str(e)
        sys.exit(2)

    if len(opts) == 0:
        print_help()
    for opt,value in opts:
        if opt == '-h':
            print_help()
        elif opt == '--file':
            filename = value
        elif opt == '--main':
            if value == '':
                print_help('MainType is [start|stop|restart|deploy|rollback]')
            else:
                mainType = value
        elif opt == '--target':
            if checkIP(value):
                target = value
            else:
                print_help('IP address 192.168.0.0/16 Need')
        elif opt == '--version':
            _version = value
        elif opt == '--ftpdir':
            if value == '':
                print_help('ftpdir default is /autodeploy')
            else:
                ftpdir = value
        elif opt == '--id':
            if value == '':
                print_help('Program number Need')
            else:
                _id = value
            
    try:
        # ��ȡָ��ID��������Ϣ
        if len(_id) == 0:
            raise ValueError("��ĿID����Ϊ��")
        _flag,dbinfo = getConf(_id)
        if not _flag:
            raise ValueError('��ȡ������Ϣʧ��:%s' % dbinfo)

        if mainType == 'deploy' or mainType == 'rollback':
            if len(filename) == 0:
                raise ValueError("�ļ�������Ϊ��")
        else:
            filename = ''
            
        # ��������·��������������
        downloaddir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),'DOWNLOAD')
        localdir = os.path.join(downloaddir,os.path.join(target,_id))
        if not os.path.isdir(localdir):
            os.makedirs(localdir)
        if mainType == 'deploy':
            getFiles(filename,localdir,ftpdir)
        else:
            print "%sģʽ�Թ�����" % (mainType)
            
        # ִ��
        _status = exec_deploy(_id,mainType,dbinfo,target,filename,_version,localdir)
        sys.exit(_status)

    except Exception,e:
        print str(e)
        sys.exit(2)
    
if __name__ == '__main__':
    main()

