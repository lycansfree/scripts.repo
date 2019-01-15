#!/app/develop/python2714/bin/python
# coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
from kafka import KafkaConsumer, TopicPartition
from multiprocessing import Pool
from elasticsearch5 import Elasticsearch
from rediscluster import StrictRedisCluster
import os
import signal
import json
import logging
import traceback
import datetime

PROCESSNUM = 2
EXPIRE = 300
basedir = os.path.dirname(os.path.abspath(__file__))
pidfile = os.path.join(basedir, '.fingw_reAIM.pid')

def consumer(i):
    csm = KafkaConsumer("fingw", bootstrap_servers = "172.20.17.69:9092", group_id = "reAIM")
    logging.basicConfig(level = logging.INFO,
            format = '%(asctime)s %(levelname)s MSG:%(message)s',
            filename = os.path.join(basedir, 'fingw.%d.log' % i),
            filemode = 'w')

    ES = Elasticsearch([
        {'host': '172.20.23.4', 'port': 9200},
        {'host': '172.20.23.5', 'port': 9200},
        {'host': '172.20.23.6', 'port': 9200},
    ])

    RD = StrictRedisCluster(startup_nodes = [
        {'host': '172.20.17.71', 'port': 7000},
        {'host': '172.20.17.71', 'port': 7001},
        {'host': '172.20.17.72', 'port': 7000},
        {'host': '172.20.17.72', 'port': 7001},
        {'host': '172.20.17.73', 'port': 7000},
        {'host': '172.20.17.73', 'port': 7001},
    ])

    for x in csm:
        try:
            tmp = json.loads(x.value)
            k = tmp['msoa.traceid'] + tmp['msoa.requestid']
            key = k + tmp['sg_flag']
            if not RD.exists(key):
                RD.hmset(key, tmp)
                RD.expire(key, EXPIRE)

            total = RD.incr(k)
            if total == 3:
                # 攒够SG_10001/SG_10002/SG_10003
                # 拿出所有的数据，聚合后插入ES，并删除所有key
                ret = {}
                for sg_flag in ('SG_10001', 'SG_10003', 'SG_10002'):
                    # update特性，导致需要将request放在最后
                    ret.update(RD.hgetall(k + sg_flag))
                # 删除对应的key
                # redis cluster client中使用循环遍历待删除key，直接写入，避开双重循环
                RD.delete(k, k + 'SG_10001', k + 'SG_10002', k + 'SG_10003')

                # UTC timezone to local
                timestamp = datetime.datetime.strptime(ret['@timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours = 8)
                index = "reaim-%s" % datetime.datetime.strftime(timestamp, '%Y.%m.%d')
                ret['@timestamp'] = datetime.datetime.strftime(timestamp, '%s%f')[:13]
                ES.index(index = index, doc_type = 'trans', body = ret)
            else:
                RD.expire(k, EXPIRE)
            
        except KeyError:
            logging.error(json.dumps(tmp, indent = 4))
            
        except Exception:
            logging.error(traceback.format_exc())

def startApp():
    pid = os.getpid()
    with open(pidfile, 'w') as f:
        f.write(str(pid))

    pool = Pool(PROCESSNUM)
    # pool.map_async(consumer, xrange(2))
    for i in xrange(PROCESSNUM):
        pool.apply_async(consumer, args = (i,))

    pool.close()
    pool.join()

def main():
    if os.path.isfile(pidfile):
        with open(pidfile, 'r') as f:
            pid = int(f.read().strip())

        with os.popen("ps --ppid %d -o pid | sed 1d" % pid) as f:
            spid = [int(x.strip()) for x in f.readlines()]
            
        spid.insert(0, pid)
    else:
        spid = []

    if sys.argv[1] == 'start':
        if len(spid) > 0:
            print "fingw already started"
            sys.exit(0)
        else:
            startApp()

    elif sys.argv[1] == 'stop':
        if len(spid) > 0:
            for x in spid:
                os.kill(x, 9)

            os.remove(pidfile)
        else:
            print "fingw already stopped"

    else:
        print sys.argv[0] + " start | stop"
    
if __name__ == '__main__':
    main()

