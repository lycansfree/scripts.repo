#!/usr/bin/env python
# coding:utf-8

import json
import yaml
import os,sys
import re

import socket
import time
import chardet
#import struct

class ZbxSender(object):
    def __init__(self,server = '127.0.0.1',host = '127.0.0.1',port = 10051,config = None):
        if config is not None:
            import re
            reServer = re.compile("^Server\s*=\s*(\d+\.\d+\.\d+\.\d+)",re.M)
            reHostname = re.compile("^Hostname\s*=\s*(.+)",re.M)
            with open(config,'r') as f:
                content = f.read()
            self.server = reServer.findall(content)[0]
            self.host = reHostname.findall(content)[0]
        else:
            self.server = server
            self.host = host

        self.port = port

        # request must be => 'sender data'
        self._packet = {
                'request':'sender data',
                'data':[]
                }

    def packMsg(self,key,value):
        tmp = {
                'host':str(self.host),
                'key':str(key),
                'value':str(value),
                'clock':int(time.time())
                }

        self._packet['data'].append(tmp)

    def cleanMsg(self):
        self._packet = {
                'request':'sender data',
                'data':[]
                }

    def sendMsg(self):
        if len(self._packet['data']) == 0:
            raise IOError('发送数据前请先打包packMsg(host,key,value)')
        else:
            _packet = json.dumps(self._packet)
            _character = chardet.detect(_packet)['encoding']
            _packet = _packet.decode(_character).encode('UTF-8')
            #packlen = len(_packet)
            #_packet = struct.pack("<4sBq" + str(packlen) + "s",'ZBXD',3,packlen,_packet)
            #print _packet

        try:
            sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sk.settimeout(3)
        except Exception,e:
            raise IOError(str(e))

        try:
            sk.connect((self.server,self.port))
            sk.send(_packet)
            #time.sleep(0.5)
            #print sk.recv(1024)
        except Exception,e:
            raise ValueError(str(e))
        finally:
            sk.close()


def get_currInfo(seekInfo,jsonID,filename):
    _fileInfo = os.stat(filename)
    if jsonID in seekInfo:
        _lastseek,_lastino = seekInfo[jsonID]
        if _lastino == _fileInfo.st_ino and _lastseek <= _fileInfo.st_size:
            # 文件未重新开始轮转且文件未被清空的
            currSeek = _lastseek
        else:
            currSeek = 0
    else:
        currSeek = 0

    return currSeek,_fileInfo.st_ino


def check_name(seekInfo,config,id,zbxsender):
    # 检查姓名
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 有中文、英文(含空格)和少数名族(含特殊符号,如·)姓名,尴尬,假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.+?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line.decode('gbk'))
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value) - 1
                # 中文转换unicode后存储为1个字符
                if _value[:-1] != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)

            # _count = len(_value) - 2
            # if _count > 0:
            #     if re.match("\*{%d}" % _count,_value):
            #         # 符合规则
            #         pass
            #     else:
            #     if 
            #         # 不符合规则,报警
            #         _status = True
            #         # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
            #         f.seek(0,2)
            # else:
            #     # 正式的姓名不应少于2个字符
            #     # 获取失败,但不影响日志脱敏
            #     pass

            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status
        

def check_IDcard(seekInfo,config,id,zbxsender):
    # 检查身份证
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.+?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                # _length = len(_value)
                if _value[6:-4] != '*' * 6:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_mobile():
    # 检查手机号
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.+?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                # _length = len(_value)
                if _value[3:-4] != '*' * 4:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_phone():
    # 检查座机
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.+?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value) - 4
                if _value[:-4] != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_addr():
    # 检查地址
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.+?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line.decode('gbk'))
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value) - 8
                if _value[:-8] != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_email():
    # 检查邮箱
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.+?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value) - 4
                if _value[4:] != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_birthday():
    # 检查生日
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.+?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value)
                if _length > 4:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_cardNo():
    # 检查卡号
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.+?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value) - 10
                if _value[6:-4] != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_amount():
    # 检查余额
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.*?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value)
                if _value != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_PWD():
    # 检查密码
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.*?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value)
                if _value != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_track2():
    # 检查磁条信息
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.*?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value)
                if _value != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_CVV():
    # 检查CVV
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.*?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value)
                if _value != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_expire():
    # 检查有效期
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.*?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value)
                if _value != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_VerifyCode():
    # 检查验证码
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.*?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value)
                if _value != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def check_photo():
    # 检查照片
    filename = config[id]["logfile"]
    jsonID = str(id)
    currSeek,currInode = get_currInfo(seekInfo,jsonID,filename)
    # 为了一次读取完整,采用_status判断
    _status = False
    # 假设日志中以英文逗号分隔
    refind = re.compile(".*?(%s):(.*?)," % config[id]['logkey'])
    with open(filename,'r') as f:
        f.seek(currSeek)
        line = f.readline()
        while line:
            res = refind.findall(line)
            if len(res) > 0:
                _key,_value = res[0]
                _length = len(_value)
                if _value != '*' * _length:
                    # 不符合规则,报警
                    _status = True
                    # 本次日志读取结束,直接跳转到日志末尾,减少性能消耗
                    f.seek(0,2)
            line = f.readline()

        seekInfo[jsonID] = (f.tell(),currInode)

    return seekInfo,_status


def main():
    zbxsender = ZbxSender(config = '/etc/zabbix/zabbix_agentd.conf')

    basedir = os.path.abspath(os.path.dirname(sys.argv[0]))
    conf = os.path.join(basedir,'zbxLog.yml')
    with open(conf,'r') as f:
        config = yaml.load(f.read().decode('gbk'))

    basekey = config["basekey"]
    logseek = os.path.join(basedir,config["logseek"])
    logIDs = config["logIDs"]
    try:
        with open(logseek,'r') as f:
            seekInfo = json.load(f)
    except Exception:
        seekInfo = {}

    for id in logIDs:
        # 传递seekInfo,config,id,zbxsender
        # check value时,可以不考虑value是否符合表达规则,如身份证是否为正确的18位,只需考虑是否在正确位置做了脱敏处理
        seekInfo,_status = eval('check_%s(seekInfo,config,id,zbxsender)' % config[id]['checktype'])
        jsonID = str(id)
        if _status:
            zbxsender.packMsg('%s[%s]' % (basekey,jsonID),'Error Exception')
        else:
            zbxsender.packMsg('%s[%s]' % (basekey,jsonID),'Success')


    # 写入seek/inode信息
    with open(logseek,'w') as f:
        json.dump(seekInfo,f)
    # 发送
    # zbxsender.sendMsg()
    # zbxsender.cleanMsg()
    # 查看测试输出,实际使用中注释
    print zbxsender._packet


if __name__ == '__main__':
    main()


