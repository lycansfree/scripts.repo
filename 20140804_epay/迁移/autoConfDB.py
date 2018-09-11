#!/usr/bin/env python
# coding:utf-8

# mysql character set is UTF-8

from mysql import connector
from datetime import datetime
import commands
import re
import os,sys
import time
import pwd,grp
import zipfile
import chardet


def alterfile(operate,filecontent,dbname,HOSTINFO,HOSTON,SERVICENAME,SERVICEON):
    _character = chardet.detect(filecontent)['encoding']
    if dbname == 'ftp':
        # add FTP/SFTP demand
        # The tentative rule here is that the FTP configuration file rule is ambiguous
        ftprep = re.compile("(.+)(%s)\D{1}" % HOSTINFO[dbname])
        ftpfind = ftprep.findall(filecontent)
        for _prefix,_name in ftpfind:
            filecontent = filecontent.replace(_prefix + _name,_prefix + HOSTON[_name].encode(_character))

    else:
        # HOST and PORT replace,attention the SERVICE_NAME
        hostrep = re.compile("(HOST\s*=\s*)(%s)(\s*\)\s*\()(PORT\s*=\s*)(1521|1522)\s*\)" % HOSTINFO[dbname],re.IGNORECASE)
        servicerep = re.compile("(SERVICE_NAME\s*=\s*)(%s)\s*\)" % SERVICENAME[dbname],re.IGNORECASE)

        # host and port
        #for _host_ in HOSTINFO[dbname].split("|"):
        #    filecontent = filecontent.replace(_host_,HOSTON[_host_])
        hostfind = hostrep.findall(filecontent)
        for _prehost,_prevalue1,_conn,_preport,_prevalue2 in hostfind:
            # filecontent = filecontent.replace(_prefix + _name,_prefix + HOSTON[_name].encode(_character))
            if dbname == 'zfcif':
                if operate == 1:
                    filecontent = filecontent.replace(_prehost + _prevalue1 + _conn + _preport + _prevalue2,_prehost + HOSTON[_prevalue1].encode(_character) + _conn + _preport + '1521')
                elif operate == 2:
                    filecontent = filecontent.replace(_prehost + _prevalue1 + _conn + _preport + _prevalue2,_prehost + HOSTON[_prevalue1].encode(_character) + _conn + _preport + '1522')
            else:
                filecontent = filecontent.replace(_prehost + _prevalue1 + _conn + _preport + _prevalue2,_prehost + HOSTON[_prevalue1].encode(_character) + _conn + _preport + _prevalue2)
        # service
        servicefind = servicerep.findall(filecontent)
        for _prefix,_name in servicefind:
            # wrong logic,should be dbname
            # filecontent = filecontent.replace(_prefix + _name,_prefix + SERVICEON[_name])
            if operate == 1 and _name == 'srvacc':
                filecontent = filecontent.replace(_prefix + _name,_prefix + 'srvacc2')
            elif operate == 2 and _name == 'srvacc2':
                filecontent = filecontent.replace(_prefix + _name,_prefix + 'srvacc')
            else:
                filecontent = filecontent.replace(_prefix + _name,_prefix + SERVICEON[dbname].encode(_character))

    return filecontent

def get_and_health(ip,_username,_password,_host,_port,_database):
    now = datetime.strftime(datetime.now(),'%Y%m%d%H%M%S')
    register_sql = "select * from healthy where ip = '%s'" % ip
    create_sql = "insert into healthy values ('%s','%s')" % (ip,now)
    update_sql = "update healthy set lastacc = '%s' where ip = '%s'" % (now,ip)

    query_sql = "select id,dbname,operate,filedir,filename,pfile from dbinfo where ip = '%s' and operate > 0" % ip

    _info = {
            'host_reg_192':{},
            'service_reg_192':{},
            'host_mapping_192':{},
            'service_mapping_192':{},
            'host_reg_172':{},
            'service_reg_172':{},
            'host_mapping_172':{},
            'service_mapping_172':{}
            }
    info_sql = "select dictname,dictkey,dictvalue from contrast_info"

    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
    except Exception,e:
        return False,str(e),_info

    try:
        cur = db.cursor()

        # update healthy time
        cur.execute(register_sql)
        res = cur.fetchall()
        if len(res) == 1:
            cur.execute(update_sql)
        else:
            cur.execute(create_sql)
        db.commit()

        # get regulation and mapping
        cur.execute(info_sql)
        res = cur.fetchall()
        for name,key,value in res:
            if name == 'host_reg_192':
                _info['host_reg_192'][key] = value
            elif name == 'service_reg_192':
                _info['service_reg_192'][key] = value
            elif name == 'host_mapping_192':
                _info['host_mapping_192'][key] = value
            elif name == 'service_mapping_192':
                _info['service_mapping_192'][key] = value
            elif name == 'host_reg_172':
                _info['host_reg_172'][key] = value
            elif name == 'service_reg_172':
                _info['service_reg_172'][key] = value
            elif name == 'host_mapping_172':
                _info['host_mapping_172'][key] = value
            elif name == 'service_mapping_172':
                _info['service_mapping_172'][key] = value
            else:
                raise ValueError('wrong name %s' % name)


        # query
        cur.execute(query_sql)
        res = cur.fetchall()
        cur.close()

        status = True

    except Exception,e:
        res = str(e)
        status = False

    finally:
        db.close()
        return status,res,_info


def startCheck(ID,dbname,operate,filedir,filename,pfile,_info):
    # create tmpdir
    tmpdir = os.path.join(basedir,'TmpConf/%s' % str(ID))
    if not os.path.isdir(tmpdir):
        os.makedirs(tmpdir)

    try:
        # get the file's user and group
        fileosinfo = os.stat(os.path.join(filedir,filename))
        username = pwd.getpwuid(fileosinfo.st_uid).pw_name
        groupname = grp.getgrgid(fileosinfo.st_gid).gr_name

        if zipfile.is_zipfile(os.path.join(filedir,filename)):
            # get file content
            filecontent = commands.getoutput("unzip -p %s %s" % (os.path.join(filedir,filename),pfile))
            # switch content
            if operate == 1:
                # update
                newcontent = alterfile(operate,filecontent,dbname,_info['host_reg_192'],_info['host_mapping_192'],_info['service_reg_192'],_info['service_mapping_192'])
            elif operate == 2:
                # rollback
                newcontent = alterfile(operate,filecontent,dbname,_info['host_reg_172'],_info['host_mapping_172'],_info['service_reg_172'],_info['service_mapping_172'])
            else:
                raise ValueError('wrong operate = %d' % operate)
            
            if filecontent != newcontent:
                _tmppfiledir = os.path.join(tmpdir,os.path.dirname(pfile))
                if not os.path.isdir(_tmppfiledir):
                    os.makedirs(_tmppfiledir)
                with open(os.path.join(tmpdir,pfile),'w') as f:
                    f.write(newcontent)
                os.chdir(tmpdir)
                # commands.getoutput('chown -R %s:%s *' % (username,groupname))
                # use the zip update,the file's user and group -> root:root
                (_s_,_o_) = commands.getstatusoutput('zip -u %s %s' % (os.path.join(filedir,filename),pfile))
                commands.getoutput('chown %s:%s %s' % (username,groupname,os.path.join(filedir,filename)))
                if _s_ > 0:
                    raise IOError('zip error %s' % _o_)
            else:
                raise ValueError('not changed!!!')

        else:
            # normal file update directly
            with open(os.path.join(filedir,filename),'r') as f:
                filecontent = f.read()
            # switch content
            if operate == 1:
                # update
                newcontent = alterfile(operate,filecontent,dbname,_info['host_reg_192'],_info['host_mapping_192'],_info['service_reg_192'],_info['service_mapping_192'])
            elif operate == 2:
                # rollback
                newcontent = alterfile(operate,filecontent,dbname,_info['host_reg_172'],_info['host_mapping_172'],_info['service_reg_172'],_info['service_mapping_172'])
            else:
                raise ValueError('wrong operate = %d' % operate)
            
            if filecontent != newcontent:
                with open(os.path.join(filedir,filename),'w') as f:
                    f.write(newcontent)
            else:
                raise ValueError('not changed!!!')

        message = 'success'

    except Exception,e:
        message = str(e)

    finally:
        return message


def reportRes(_localIP,_username,_password,_host,_port,_database,missions):
    try:
        db = connector.connect(user = _username,password = _password,host = _host,port = _port,database = _database)
    except Exception,e:
        return False,str(e)

    try:
        cur = db.cursor()

        cur.executemany("update dbinfo set operate = 0 , lastoperate = %s , lastoutput = %s , lasttime = %s where id = %s",missions)
        db.commit()
        cur.close()

        status = True
        res = "exec successfully"

    except Exception,e:
        res = str(e)
        status = False

    finally:
        db.close()
        return status,res

def errorLog(line):
    with open(os.path.join(basedir,'dbconf_error.log'),'a') as f:
        f.write(line + '\n')

def main():
    _username = 'bjfuzj'
    _password = 'Nagi_!22*'
    _host = '192.168.80.109'
    _port = 6666
    _database = 'migrate'
    # get local IP
    # import socket
    # _localIP = socket.gethostbyname(socket.gethostname())
    o = commands.getoutput('ifconfig')
    rep = re.compile("inet addr:(192\.168\.\d+\.\d+)")
    _localIP = rep.findall(o)[0]

    global basedir
    #basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    basedir = '/app/saltTMP'

    # begin
    status,res,_info = get_and_health(_localIP,_username,_password,_host,_port,_database)
    if status:
        # get succ
        if len(res) > 0:
            missions = []
            # exist mission,call startCheck
            for ID,dbname,operate,filedir,filename,pfile in res:
                message = startCheck(ID,dbname,operate,filedir,filename,pfile,_info)
                now = datetime.strftime(datetime.now(),'%Y%m%d%H%M%S')
                missions.append((operate,message,now,ID))

            ss,output = reportRes(_localIP,_username,_password,_host,_port,_database,missions)
            if not ss:
                #errorLog(o)
                print output
                sys.exit(3)
    else:
        #errorLog(res)
        print res
        sys.exit(2)


if __name__ == '__main__':
    main()
    
