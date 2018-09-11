#!/usr/bin/env python
# coding:utf-8

import paramiko
from ftplib import FTP
import cx_Oracle
import os,sys
import socket
import datetime
import logging,logging.config


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

def sftp_handle(host,username,password,remotedir,localdir,filename,action):
    try:
        status = 0
        ssh = GET_exit_status()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host,username=username,password=password)
        sftp = ssh.open_sftp()
        # 切换到本地路径
        if os.path.isdir(localdir):
            os.chdir(localdir)
        else:
            os.makedirs(localdir)

        sftp.chdir(remotedir)

        if action == 'put':
            # 从本地上传
            sftp.put(filename,filename)
            stdin,stdout,stderr,stdchan = ssh.exec_command('ls ' + os.path.join(remotedir,filename))
            if int(stdchan.recv_exit_status()) != 0:
                raise IOError(filename + '上传失败')

            translogger.info(filename + '上传成功')

        elif action == 'get':
            # 从远端下载
            sftp.get(filename,filename)
            if not os.path.isfile(filename):
                raise IOError(filename + '下载失败')

            translogger.info(filename + '下载成功')

        sftp.close()
        ssh.close()

    except Exception,e:
        status = 1
        errorlogger.error(str(e))

    finally:
        return status

def ftp_handle(host,username,password,remotedir,localdir,filename,action):
    try:
        status = 0
        buffsize = 4096
        # 切换到本地路径
        if os.path.isdir(localdir):
            os.chdir(localdir)
        else:
            os.makedirs(localdir)

        # 登录ftp
        ftp = FTP(host)
        ftp.login(username,password)
        # 切换到远端路径
        ftp.cwd(remotedir)
        # 判断上传还是下载
        if action == 'put':
            # 从本地上传
            with open(filename,'rb') as f:
                ftp.storbinary('STOR' + filename,f,buffsize)
            if filename not in ftp.nlst():
                raise IOError(filename + '上传失败')

            translogger.info(filename + '上传成功')

        elif action == 'get':
            # 从远端下载
            with open(filename,'wb') as f:
                ftp.retrbinary('RETR' + filename,f.write,buffsize)
            if not os.path.isfile(filename):
                raise IOError(filename + '下载失败')

            translogger.info(filename + '下载成功')

        ftp.close()

    except Exception,e:
        status = 1
        errorlogger.error(str(e))

    finally:
        return status
    

def trans_action(missions):
    global lock
    global execList
    for ID,today,filename,transtamp,fromtype,fromhost,fromuser,frompass,fromdir,totype,tohost,touser,topass,todir,laststatus,exec_times,localdir in missions:
        # 执行次数+1
        exec_times += 1
        # 先下载
        if fromtype == 'ftp':
            ss = ftp_handle(fromhost,fromuser,frompass,fromdir,localdir,filename,'get')
        elif fromtype == 'sftp':
            ss = sftp_handle(fromhost,fromuser,frompass,fromdir,localdir,filename,'get')

        if ss != 0:
            # 获取锁
            lock.acquire()
            execList.append((laststatus,exec_times,ID,today))
            # 释放锁
            lock.release()
            continue
        
        # 后上传
        if totype == 'ftp':
            ss = ftp_handle(tohost,touser,topass,todir,localdir,filename,'put')
        elif totype == 'sftp':
            ss = sftp_handle(tohost,touser,topass,todir,localdir,filename,'put')

        if ss == 0:
            # 下载和上传都成功了,则成功
            laststatus = 1

        # 获取锁
        lock.acquire()
        execList.append((laststatus,exec_times,ID,today))
        # 释放锁
        lock.release()

# 分组,核心算法,用于分配多个任务
# 分配给传输器以及多线程I/O任务
def groups(array,threads):
    try:
        status = 0
        lenth = len(array)
        if lenth == 0 or threads == 0:
            raise ValueError('待划分数组或线程数不能为0')

        boundary = lenth / threads
        remainder = lenth % threads
        res = []
        if boundary == 0:
            res.append(array)
        else:
            for i in range(threads):
                if boundary * (i + 1) + remainder == lenth:
                    res.append(array[boundary*i:])
                else:
                    res.append(array[boundary*i:boundary*(i+1)])

    except Exception,e:
        status = 1
        errorlogger.critical(str(e))
        res = []

    finally:
        return status,res

def get_alive(local_id,username,password,sid):
    # 先获取所有的IP列表
    # 根据列表做探测,如果自身ID不在列表中,说明尚未注册,不参与传输服务
    sql = "select * from register"
    living_host = []
    try:
        db = cx_Oracle.connect(username,password,sid)
        cur = db.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        db.close()

        status = 1
        for host,port in res:
            if host == local_id:
                # 说明已注册
                status = 0
            else:
                # 探测接口存活
                ss = probe_alive(host,port)
                if ss == 0:
                    living_host.append(host)

    except Exception,e:
        errorlogger.error(str(e))

    finally:
        return status,living_host


def probe_alive(host,port):
    try:
        sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sk.settimeout(2)
        sk.connect((host,port))
        probe_string = 'status'
        sk.send(probe_string)
        buffsize = 1024
        return_string = sk.recv(buffsize)
        if return_string == 'running':
            status = 0
            translogger.info(host + ' ' + return_string)
        else:
            status = 1
            errorlogger.error(host + ' ' + return_string)

        sk.close()

    except socket.timeout:
        status = 2
        errorlogger.critical(host + '连接超时')

    except Exception,e:
        status = 3
        errorlogger.critical(host + '异常:' + str(e))

    finally:
        return status


def get_res(username,password,sid,living_num,local_id_index):
    sql = '''
        select * from transfer where laststatus = 0 and exec_times < 3 order by today,ID
        '''
    try:
        status = 0
        db = cx_Oracle.connect(username,password,sid)
        cur = db.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        db.close()

        if len(res) == 0:
            raise ValueError('待执行任务数为0')
        else:
            ss,group_res = groups(res,living_num)
            if ss == 0:
                if len(group_res) > local_id_index:
                    return_res = group_res[local_id_index]
                    translogger.info('INDEX-%d分配任务成功' % local_id_index)
                else:
                    raise ValueError('INDEX-%d未分配到任务' % local_id_index)
            else:
                raise ValueError('核心分组算法异常')

    except Exception,e:
        status = 1
        return_res = []
        errorlogger.error(str(e))

    finally:
        return status,return_res


# 开启多线程传输任务
def loop(missions,username,password,sid):
    #
    tList = []
    for mission in missions:
        t = threading.Thread(target = trans_action,args = (mission,))
        tList.append(t)

    # 启动
    for t in tList:
        t.setDaemon(True)
        t.start()

    # 阻塞
    for t in tList:
        t.join()

    # 执行完成后获取
    global execList
    try:
        db = cx_Oracle.connect(username,password,sid)
        cur = db.cursor()
        cur.executemany("update transfer set laststatus = ?,exec_times = ? where ID = ? and today = '?'",execList)
        db.commit()
        cur.close()
        db.close()

    except Exception,e:
        errorlogger.critical('更新出现异常:' + str(e))
    

def listen_handle(client,addr):
    buffsize = 1024
    recv_data = client.recv(buffsize)
    if recv_data.strip('\n\r') == 'status':
        global piddir
        with open(os.path.join(piddir,'trans.pid'),'r') as f:
            pid = int(f.read().strip('\n\r'))
        with open(os.path.join(piddir,'exec.time'),'r') as f:
            last_exec = f.read().strip('\n\r')

        try:
            os.kill(pid,0)
            now = datetime.datetime.now()
            tmp = (now - datetime.datetime.strptime(last_exec,'%Y%m%d %H:%M:%S')).seconds
            if tmp > 3600:
                raise ValueError('距离上次执行时间超过1小时')
        except OSError:
            send_data = 'Process Shutdown'
            errorlogger.critical('进程%d已停' % pid)
        except ValueError,e:
            send_data = 'exec timeout(3600s)'
            errorlogger.critical(str(e))
        except Exception,e:
            send_data = 'unknown exception'
            errorlogger.critical(str(e))
    else:
        send_data = 'unknown question'
        translogger.warn('%s发起未知的查询' % addr)

    client.send(send_data)
    client.close()


def listen_main(local_id):
    # 监听进程的主函数
    # 记录pid,探测执行时间和当前时间的差异
    global piddir
    listen_pid = str(os.getpid())
    with open(os.path.join(piddir,'listen.pid'),'w') as f:
        f.write(listen_pid)
    
    port = 3664
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 端口地址复用,防止连接关闭后,在TIME_WAIT状态时无法再绑定
    sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sk.bind((local_id,port))
    sk.listen(0)
    while True:
        client,addr = sk.accept()
        t = threading.Thread(target = listen_handle,args = (client,addr))
        t.start()

def trans_main(local_id):
    # 传输进程的主函数
    # 记录pid和执行时间
    username = 'ftp_push_info'
    password = 'le9xIOCK!#'
    sid = 'zfoms'
    # 设定任务执行间隔,单位秒
    interval = 60

    # 写入pid
    global piddir
    trans_pid = str(os.getpid())
    with open(os.path.join(piddir,'trans.pid'),'w') as f:
        f.write(trans_pid)

    while True:
        # 写入执行时间
        now = datetime.datetime.now()
        current = datetime.datetime.strftime(now,'%Y%m%d %H:%M:%S')
        with open(os.path.join(piddir,'exec.time'),'r') as f:
            lastwrite = f.read().strip('\n\r')
        # 先写入最新的,然后比对旧的,判断是否要跳过执行
        with open(os.path.join(piddir,'exec.time'),'w') as f:
            f.write(current)

        if (now - datetime.datetime.strptime(lastwrite,'%Y%m%d %H:%M:%S')).seconds > 3600:
            time.sleep(600)
            translogger.warn('距离上次执行已过一小时,本次暂停10分钟确保任务分配正常')
            continue

        ss,living_host = get_alive(local_id,username,password,sid)
        if ss == 1:
            errorlogger.critical(local_id + '未在register表中注册')
            time.sleep(interval)
            continue
        else:
            living_host.append(local_id)
            living_host.sort()
            local_id_index = living_host.index(local_id)
            living_num = len(living_host)
            translogger.info('存活的传输器共%d个:%s' % (living_num,','.join(living_host)))
            ss,missions = get_res(username,password,sid,living_num,local_id_index)
            if ss == 1:
                translogger.warn('当前传输器未分配任务,等待%d秒' % interval)
                time.sleep(interval)
                continue
            else:
                global execList
                # 初始化全局列表
                execList = []

                # 指定线程数
                threadsNUM = 5
                # 分组任务
                ss,missionTN = groups(missions,threadsNUM)
                if ss == 0:
                    loop(missionTN,username,password,sid)
                else:
                    errorlogger.critical('核心分组算法异常')


        time.sleep(interval)


def main():
    # 单条只记录一个文件,不支持多个文件连续上传下载,否则有异常不好排查
    # 获取本机IP
    # localIP = socket.gethostbyname(socket.gethostname())
    # 获取本机IP列表
    # localIPList = socket.gethostbyname_ex(socket.gethostname())
    local_id = '192.168.11.72'





if __name__ == '__main__':
    # 全局变量,存储执行结果,更新laststatus和exec_times
    execList = []
    # 锁对象
    lock = threading.Lock()
    # 存储路径
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    # 配置路径
    confdir = os.path.join(basedir,'config')
    # pid路径
    piddir = os.path.join(basedir,'running')
    # 文件存储路径
    stordir = os.path.join(basedir,'storFiles')

    # 先校验相关的路径和文件是否存在
    if os.path.isdir(confdir):
        os.makedirs(confdir)
    if os.path.isdir(piddir):
        os.makedirs(piddir)
    if os.path.isdir(stordir):
        os.makedirs(stordir)

    # 初始化日志
    logconfig = os.path.join(confdir,'logging.properties')
    logging.config.fileConfig(logconfig)
    translogger = logging.getLogger('transLog')
    errorlogger = logging.getLogger('errorLog')

    # 执行
    main()

