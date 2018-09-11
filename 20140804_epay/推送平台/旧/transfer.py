#!/usr/bin/env python
# coding:utf-8

import paramiko
from ftplib import FTP
import cx_Oracle
import os,sys
import socket
import time,datetime
import logging,logging.config
import threading
# import multiprocessing


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

def get_alive(localIP,username,password,sid):
    # 先获取所有的IP列表
    # 根据列表做探测,如果自身ID不在列表中,说明尚未注册,不参与传输服务
    sql = "select * from register"
    living_host = []
    living_time = []
    status = 1
    try:
        db = cx_Oracle.connect(username,password,sid)
        cur = db.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        db.close()

        for host,port in res:
            if host == localIP:
                # 说明已注册
                status = 0
            else:
                # 探测接口存活
                ss,tt = probe_alive(host,port)
                if ss == 0:
                    living_host.append(host)
                    living_time.append(tt)

    except Exception,e:
        errorlogger.error(str(e))

    finally:
        return status,living_host,living_time


def probe_alive(host,port):
    try:
        sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sk.settimeout(2)
        sk.connect((host,port))
        probe_string = 'status'
        sk.send(probe_string)
        buffsize = 1024
        return_string = sk.recv(buffsize)
        if return_string == 'Zombie':
            status = 1
            errorlogger.error(host + '工作进程僵尸')
        elif return_string == 'un_exp':
            status = 1
            errorlogger.error(host + '工作进程未知异常')
        elif return_string == 'un_qst':
            status = 1
            errorlogger.critical('本机发起了错误查询')
        else:
            status = 0
            translogger.info(host + '工作进程最近一次开始时间:' + return_string)

        sk.close()

    except socket.timeout:
        status = 2
        return_string = 'Timeout'
        errorlogger.critical(host + '连接超时')

    except Exception,e:
        status = 3
        return_string = 'unknown E'
        errorlogger.critical(host + '异常:' + str(e))

    finally:
        return status,return_string


def get_res(username,password,sid,living_num,localIP_index):
    sql = '''
        select * from transfer where laststatus = 0 and exec_times < 3 and transtamp < to_char(SYSDATE,'YYYYMMDD HH24:MI:SS') order by today,ID
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
                if len(group_res) > localIP_index:
                    return_res = group_res[localIP_index]
                    translogger.info('INDEX-%d分配任务成功' % localIP_index)
                else:
                    raise ValueError('INDEX-%d未分配到任务' % localIP_index)
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
    try:
        db = cx_Oracle.connect(username,password,sid)
        cur = db.cursor()
        cur.executemany("update transfer set laststatus = :1,exec_times = :2 where ID = :3 and today = ':4'",execList)
        db.commit()
        cur.close()
        db.close()

    except Exception,e:
        errorlogger.critical('更新出现异常:' + str(e))
    
# 计算文件存储路径的总大小,和之前比较,判断worker是否存活
def dusb():
    total = 0
    for root,dirs,filenames in os.walk(stordir):
        total += 4096
        for filename in filenames:
            total += os.path.getsize(os.path.join(root,filename))

    return total

def listen_handle(client,addr):
    buffsize = 1024
    recv_data = client.recv(buffsize)
    if recv_data.strip('\n\r') == 'status':
        with open(pid_status,'r') as f:
            lastline = f.read().strip('\n\r').split()
            lastEtime = lastline[0]
            lastEsize = lastline[1]

        try:
            currEtime = datetime.datetime.strftime(datetime.datetime.now(),'%s')
            currEsize = dusb()
            if int(currEtime) - int(lastEtime) > 600 and int(lastEsize) == currEsize:
                raise ValueError('执行时间已超过10分钟且本地文件大小无变化,判定worker变僵尸')
            send_data = lastEtime
        except ValueError,e:
            send_data = 'Zombie'
            errorlogger.critical(str(e))
        except Exception,e:
            send_data = 'un_exp'
            errorlogger.critical(str(e))
    else:
        send_data = 'un_qst'
        translogger.warn('%s发起未知的查询' % addr)

    client.send(send_data)
    client.close()


def listen_main(localIP):
    # 监听进程的主函数
    # 记录pid,探测执行时间和当前时间的差异
    port = 3664
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 端口地址复用,防止连接关闭后,在TIME_WAIT状态时无法再绑定
    sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sk.bind((localIP,port))
    sk.listen(0)
    while True:
        client,addr = sk.accept()
        t = threading.Thread(target = listen_handle,args = (client,addr))
        t.start()

def trans_main(localIP):
    # 初始化标志
    initFlg = 0
    # 传输进程的主函数
    # 记录pid和执行时间
    username = 'ftp_push_info'
    password = 'le9xIOCK!#'
    sid = 'zfoms'
    # 设定任务执行间隔,单位秒
    interval = 60

    while True:
        # 写入执行时间
        currEtime = datetime.datetime.strftime(datetime.datetime.now(),'%s')
        currEsize = dusb()
        with open(pid_status,'w') as f:
            f.write(currEtime + ' ' + str(currEsize))

        ss,living_host,living_time = get_alive(localIP,username,password,sid)
        if ss == 1:
            errorlogger.critical(localIP + '未在register表中注册')
            time.sleep(interval)
            continue

        else:
            if initFlg == 0:
                # 改变初始化标志,代表已经启动
                initFlg = 1
                translogger.info('worker初始化启动,等待%s全部执行完成' % ','.join(living_host))
                # 需要等待所有存活的worker执行完当前任务,确保不会由于启动导致重复执行
                while True:
                    ss,living_host,living_time_n = get_alive(localIP,username,password,sid)
                    cc = 0
                    for lvt in living_time:
                        if lvt in living_time_n:
                            # 只要有时间重复,代表有worker没执行完当前任务
                            time.sleep(interval)
                            break
                        else:
                            cc += 1
                    if cc == len(living_time):
                        break

            living_host.append(localIP)
            living_host.sort()
            localIP_index = living_host.index(localIP)
            living_num = len(living_host)
            translogger.info('存活的传输器共%d个:%s' % (living_num,','.join(living_host)))
            ss,missions = get_res(username,password,sid,living_num,localIP_index)
            if ss == 1:
                translogger.warn('当前传输器未分配任务,等待%d秒' % interval)
                time.sleep(interval)
                continue
            else:
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
    localIP = '192.168.11.72'

    #################################################################################
    global execList,lock
    global pid_status
    global stordir
    global translogger,errorlogger

    # 全局变量,存储执行结果,更新laststatus和exec_times
    execList = []
    # 锁对象
    lock = threading.Lock()
    # 存储路径
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    # 配置路径
    confdir = os.path.join(basedir,'config')
    # 日志路径
    logdir = os.path.join(basedir,'logs')
    # pid路径
    piddir = os.path.join(basedir,'running')
    pid_main = os.path.join(piddir,'main.pid')
    pid_status = os.path.join(piddir,'exec.status')

    # 文件存储路径
    stordir = os.path.join(basedir,'storFiles')

    # 先校验相关的路径和文件是否存在
    if not os.path.isdir(confdir):
        os.makedirs(confdir)
    if not os.path.isdir(piddir):
        os.makedirs(piddir)
    if not os.path.isdir(stordir):
        os.makedirs(stordir)
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
    # 每次启动时初始化状态文件
    with open(pid_status,'w') as f:
        currEtime = datetime.datetime.strftime(datetime.datetime.now(),'%s')
        currEsize = dusb()
        f.write(currEtime + ' ' + str(currEsize))

    # 初始化日志
    logconfig = os.path.join(confdir,'logging.properties')
    logging.config.fileConfig(logconfig)
    translogger = logging.getLogger('transLog')
    errorlogger = logging.getLogger('errorLog')

    #################################################################################

    PID = str(os.getpid())
    with open(pid_main,'w') as f:
        f.write(PID)

    tList = []
    # tList.append(multiprocessing.Process(target = trans_main,args = (localIP,)))
    # tList.append(multiprocessing.Process(target = listen_main,args = (localIP,)))
    tList.append(threading.Thread(target = trans_main,args = (localIP,)))
    tList.append(threading.Thread(target = listen_main,args = (localIP,)))
    for t in tList:
        t.start()




if __name__ == '__main__':
    main()

