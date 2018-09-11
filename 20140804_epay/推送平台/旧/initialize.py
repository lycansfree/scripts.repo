#!/usr/bin/env python
# coding:utf-8

import cx_Oracle
import os,sys
import datetime

def sql_handle(stordir):
    sid = 'zfoms'
    username = 'FTP_PUSH_INFO'
    password = 'le9xIOCK!#'
    now = datetime.datetime.now()
    today = datetime.datetime.strftime(now,'%Y%m%d')
    query_sql = "select * from template where ID not in (select ID from transfer where today = %s)" % today
    try:
        status = 0
        db = cx_Oracle.connect(username,password,sid)
        cur = db.cursor()
        cur.execute(query_sql)
        res = cur.fetchall()

        insert_array = []
        result = []
        for ID,fromtype,fromhost,fromuser,frompass,fromdir,totype,tohost,touser,topass,todir,filename,daytype,offset,transtamp,remark in res:
            timestamp = datetime.datetime.strftime((now + datetime.timedelta(days = offset)),daytype)
            filename = filename.replace('YYYYMMDD',timestamp)
            transtamp = today + ' ' + transtamp
            localdir = stordir + '/' + today + '/' + str(ID)
            insert_array.append((ID,today,filename,transtamp,fromtype,fromhost,fromuser,frompass,fromdir,totype,tohost,touser,topass,todir,0,0,localdir))
            result.append(localdir)

        cur.executemany("insert into transfer values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",insert_array)
        db.commit()

        cur.close()
        db.close()

    except Exception,e:
        status = 1
        result = str(e)

    finally:
        return status,result

def rm_old_files(stordir):
    offset = 7
    old_day = datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days = offset)),'%Y%m%d')
    os.chdir(stordir)
    if os.path.isdir(old_day):
        # 超过设定时间的目录需要删除
        import shutil
        shutil.rmtree(old_day)

def main():
    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    stordir = os.path.join(basedir,'storFiles')
    ss,res = sql_handle(stordir)
    if ss == 1:
        print "推送平台生成执行表信息失败:" + res
        sys.exit(3)

    rm_old_files(stordir)


if __name__ == '__main__':
    main()
