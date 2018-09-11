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
import json


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
            os.chdir(localdir)

        sftp.chdir(remotedir)

        if action == 'put':
            # 从本地上传
            sftp.put(filename,filename)
            stdin,stdout,stderr,stdchan = ssh.exec_command('ls ' + os.path.join(remotedir,filename))
            if int(stdchan.recv_exit_status()) != 0:
                raise IOError(filename + '上传失败')
            if sftp.lstat(filename).st_size != os.path.getsize(filename):
                raise IOError(filename + '上传后大小不一致')

            translogger.info(filename + '上传成功')

        elif action == 'get':
            # 从远端下载
            stdin,stdout,stderr,stdchan = ssh.exec_command('ls ' + os.path.join(remotedir,filename))
            if int(stdchan.recv_exit_status()) != 0:
                raise IOError(filename + '不存在,无法下载')

            sftp.get(filename,filename)
            if not os.path.isfile(filename):
                raise IOError(filename + '下载失败')
            if sftp.lstat(filename).st_size != os.path.getsize(filename):
                raise IOError(filename + '下载后大小不一致')

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
            os.chdir(localdir)

        # 登录ftp
        ftp = FTP(host)
        ftp.login(username,password)
        # 切换到远端路径
        ftp.cwd(remotedir)
        # 判断上传还是下载
        if action == 'put':
            # 从本地上传
            with open(filename,'rb') as f:
                ftp.storbinary('STOR ' + filename,f,buffsize)
            if filename not in ftp.nlst():
                raise IOError(filename + '上传失败')
            if ftp.size(filename) != os.path.getsize(filename):
                raise IOError(filename + '上传后文件大小不一致')

            translogger.info(filename + '上传成功')

        elif action == 'get':
            # 从远端下载
            if filename not in ftp.nlst():
                raise IOError(filename + '不存在,无法下载')

            with open(filename,'wb') as f:
                ftp.retrbinary('RETR' + filename,f.write,buffsize)
            if not os.path.isfile(filename):
                raise IOError(filename + '下载失败')
            if ftp.size(filename) != os.path.getsize(filename):
                raise IOError(filename + '下载后文件大小不一致')

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
            # lock.acquire()
            execList.append((laststatus,exec_times,ID,today))
            # 释放锁
            # lock.release()
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
        # 列表的append,不需要顺序,所以不需要加锁
        # lock.acquire()
        execList.append((laststatus,exec_times,ID,today))
        # 释放锁
        # lock.release()

# 分组,核心算法,用于分配多个任务
# 分配给传输器以及多线程I/O任务
def groups(array,threads):
    try:
        status = 0
        lenth = len(array)
        if lenth == 0 or threads == 0:
            raise ZeroDivisionError('待划分数组或线程数不能为0')

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

    except ZeroDivisionError,e:
        status = 1
        errorlogger.critical(str(e))
        res = []
        
    except Exception,e:
        status = 2
        errorlogger.critical(str(e))
        res = []

    finally:
        return status,res

def get_alive(localIP,localPort,username,password,sid):
    # 先获取所有的IP列表
    # 根据列表做探测,如果自身ID不在列表中,说明尚未注册,不参与传输服务
    sql = "select * from register"
    living_host = []
    living_time = []
    reg_res = {}
    status = 1
    try:
        db = cx_Oracle.connect(username,password,sid)
        cur = db.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        cur.close()
        db.close()

        for ID,host,port in res:
            reg_res[ID] = host
            if host == localIP and port == localPort:
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
        return status,living_host,living_time,reg_res


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


def get_res(username,password,sid,living_host,reg_res,localIP):
    try:
        for localIndex in reg_res:
            if reg_res[localIndex] == localIP:
                break
        # 获取结果,判断是否需要接管
        reg_res_length = len(reg_res)
        tmp_range = reg_res_length - len(living_host)

        sqls = []
        sql = "select * from transfer a where a.laststatus = 0 and a.exec_times < 3 and a.transtamp < to_char(SYSDATE,'YYYYMMDD HH24:MI:SS') and mod(a.ID,%d) = %d" % (reg_res_length,localIndex)
        sqls.append(sql)

        translogger.info('判断是否需要接管')
        if tmp_range > 0:
            for i in range(tmp_range):
                # 向后探测并尝试接管,若存活,则退出
                currIndex = (localIndex + i + 1) % reg_res_length
                if reg_res[currIndex] in living_host:
                    break
                else:
                    translogger.warn('接管传输器%s' % reg_res[currIndex])
                    sql = "select * from transfer a where a.laststatus = 0 and a.exec_times < 3 and a.transtamp < to_char(SYSDATE,'YYYYMMDD HH24:MI:SS') and mod(a.ID,%d) = %d" % (reg_res_length,currIndex)
                    sqls.append(sql)
        translogger.info('接管完成,开始获取任务')
                
        status = 0
        # 打开连接
        db = cx_Oracle.connect(username,password,sid)
        cur = db.cursor()

        result = []
        for sql in sqls:
            cur.execute(sql)
            res = cur.fetchall()
            result += res

        cur.close()
        db.close()

        translogger.info('本次共执行%d个任务' % len(result))

    except Exception,e:
        status = 1
        result = []
        errorlogger.error(str(e))

    finally:
        return status,result


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
        cur.executemany("update transfer set laststatus = :1,exec_times = :2 where ID = :3 and today = :4",execList)
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


def listen_main(localIP,localPort):
    # 监听进程的主函数
    # 记录pid,探测执行时间和当前时间的差异
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 端口地址复用,防止连接关闭后,在TIME_WAIT状态时无法再绑定
    sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sk.bind((localIP,localPort))
    sk.listen(0)
    while True:
        client,addr = sk.accept()
        t = threading.Thread(target = listen_handle,args = (client,addr))
        t.start()

def trans_main(localIP,localPort,username,password,sid,interval,threadsNUM):
    # 初始化标志
    initFlg = 0
    # 传输进程的主函数
    # 记录pid和执行时间

    while True:
        # 写入执行时间
        currEtime = datetime.datetime.strftime(datetime.datetime.now(),'%s')
        currEsize = dusb()
        with open(pid_status,'w') as f:
            f.write(currEtime + ' ' + str(currEsize))

        ss,living_host,living_time,reg_res = get_alive(localIP,localPort,username,password,sid)
        if ss == 1:
            errorlogger.critical(localIP + '未在register表中注册')
            translogger.warn('[%s]未注册,等待%d秒' % (currEtime,interval))
            time.sleep(interval)
            continue

        else:
            if initFlg == 0:
                # 改变初始化标志,代表已经启动
                initFlg = 1
                translogger.info('worker初始化启动,等待%s全部执行完成' % ','.join(living_host))
                # 需要等待所有存活的worker执行完当前任务,确保不会由于启动导致重复执行
                while True:
                    ss,living_host,living_time_n,reg_res = get_alive(localIP,localPort,username,password,sid)
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
            translogger.info('存活的传输器共%d个:%s' % (len(living_host),','.join(living_host)))
            # get_res 改为接管模式
            ss,missions = get_res(username,password,sid,living_host,reg_res,localIP)
            if ss == 1:
                translogger.warn('[%s]传输器获取任务失败,等待%d秒' % (currEtime,interval))
                time.sleep(interval)
                continue
            else:
                # 初始化全局列表
                execList = []

                # 分组任务
                ss,missionTN = groups(missions,threadsNUM)
                if ss == 0:
                    loop(missionTN,username,password,sid)
                elif ss == 1:
                    translogger.info('[%s]无任务' % currEtime)
                elif ss == 2:
                    errorlogger.critical('核心分组算法异常')


        translogger.info('[%s]任务完成,等待%d秒' % (currEtime,interval))
        time.sleep(interval)


def main():
    try:
        # 单条只记录一个文件,不支持多个文件连续上传下载,否则有异常不好排查

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

        # 获取本机IP
        # localIP = socket.gethostbyname(socket.gethostname())
        # 获取本机IP列表
        # localIPList = socket.gethostbyname_ex(socket.gethostname())
        _localIP = socket.gethostbyname(socket.gethostname())
        with open(os.path.join(confdir,'conf.properties'),'r') as f:
            res = f.read()
        ConfigAll = json.loads(res)
        username = ConfigAll['username']
        password = ConfigAll['password']
        sid = ConfigAll['sid']
        localIP = ConfigAll['localIP'].encode('utf-8')
        localPort = ConfigAll['localPort']
        # 设定任务执行间隔,单位秒
        interval = ConfigAll['interval']
        # 指定线程数
        threadsNUM = ConfigAll['threadsNUM']

        if _localIP != localIP:
            raise ValueError('请校验localIP:%s' % _localIP)

        #################################################################################

        PID = str(os.getpid())
        with open(pid_main,'w') as f:
            f.write(PID)

        tList = []
        # tList.append(multiprocessing.Process(target = trans_main,args = (localIP,)))
        # tList.append(multiprocessing.Process(target = listen_main,args = (localIP,)))
        tList.append(threading.Thread(target = trans_main,args = (localIP,localPort,username,password,sid,interval,threadsNUM)))
        tList.append(threading.Thread(target = listen_main,args = (localIP,localPort)))
        for t in tList:
            t.start()

    except Exception,e:
        errorlogger.critical('启动异常,退出:' + str(e))
        sys.exit(2)


if __name__ == '__main__':
    main()


