#!/usr/bin/env python
# coding:utf-8

# 创建相关数据表,使用sqlite3
# CREATE TABLE info (basedir varchar(50),filename varchar(50),mtime varchar(14),size varchar(50),primary key(basedir,filename));

from ftplib import FTP
import sqlite3
import os,sys
import re
import datetime


class MYFTP(FTP):
    def retrlines(self, cmd):
        # 修改callback
        CRLF = '\r\n'

        resp = self.sendcmd('TYPE A')
        conn = self.transfercmd(cmd)
        fp = conn.makefile('rb')
        lines = ''
        while 1:
            line = fp.readline()
            if self.debugging > 2: print '*retr*', repr(line)
            if not line:
                break
            if line[-2:] == CRLF:
                line = line[:-2]
            elif line[-1:] == '\n':
                line = line[:-1]
            #callback(line)
            lines += line + '\n'
            
        fp.close()
        conn.close()
        return lines,self.voidresp()

def print_color(message,color):
    # print "%s[0;32;1m test %s[0m" % (chr(27),chr(27))
    colors = {
            'green':'\033[0;32;1m',
            'yellow':'\033[0;33;1m',
            'red':'\033[0;31;1m',
            'white':'\033[0m'
            } 
    print "%s%s\033[0m" % (colors[color],message)

def loop(db,ftp,basedir,subdir):
    _basedir_ = os.path.join(basedir,subdir)
    ftp.cwd(_basedir_)
    res,rresp = ftp.retrlines('MLSD')

    reqf = recpf.findall(res)
    reqd = recpd.findall(res)

    cur = db.cursor()
    cur.execute("select filename,mtime from info where basedir = '%s'" % _basedir_)
    dbres = cur.fetchall()
    cur.execute("delete from info where basedir = '%s'" % _basedir_)

    if len(reqf) > 0:
        print_color(_basedir_,'yellow')
    for __size,__mtime,__filename in reqf:
        _mtime_ = datetime.datetime.strftime(datetime.datetime.strptime(__mtime,'%Y%m%d%H%M%S') + \
                    datetime.timedelta(hours = 8),'%Y%m%d %H:%M:%S')
        if (__filename,__mtime) not in dbres:
            print_color('文件名:%-40s\t文件大小:%-40s\t修改时间:%-20s' % (__filename,__size,_mtime_),'red')
        else:
            print_color('文件名:%-40s\t文件大小:%-40s\t修改时间:%-20s' % (__filename,__size,_mtime_),'white')
        
        cur.execute("insert into info values ('%s','%s','%s','%s')" % (_basedir_,__filename,__mtime,__size))
    db.commit()
    cur.close()

    for _time,_basedir in reqd:
        loop(db,ftp,_basedir_,_basedir)


def main():
    global recpf,recpd
    recpf = re.compile("Type=file;Size=(.+);Modify=(.+);Win32.ea=.+; (.+)")
    recpd = re.compile("Type=dir;Modify=(.+);Win32.ea=.+; (.+)")

    host = '192.168.7.244'
    username = 'unicompay'
    password = 'unicompay'
    basedir = '/'
    subdir = 'autodeploy'
    db = sqlite3.connect(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),'._ftpInfo.sqlite3'))

    ftp = MYFTP(host)
    ftp.login(username,password)
    loop(db,ftp,basedir,subdir)

    ftp.close()
    db.close()

if __name__ == '__main__':
    main()

