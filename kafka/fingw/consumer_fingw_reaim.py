#!/mnt/develop/py27/bin/python
# coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
from confluent_kafka import Consumer, KafkaError
from elasticsearch5 import Elasticsearch
from rediscluster import StrictRedisCluster
import os
import signal
import json
import logging
import logging.config
import traceback
import datetime

EXPIRE = 600
# basedir = os.path.dirname(os.path.abspath(__file__))
RUNNING = True

ES = Elasticsearch([
    {'host': '172.17.4.4', 'port': 9200},
    {'host': '172.17.4.5', 'port': 9200},
    {'host': '172.17.4.6', 'port': 9200},
])

RD = StrictRedisCluster(startup_nodes = [
    {'host': '10.1.160.19', 'port': 7000},
    {'host': '10.1.160.19', 'port': 7001},
    {'host': '10.1.161.18', 'port': 7000},
    {'host': '10.1.161.18', 'port': 7001},
    {'host': '10.1.162.38', 'port': 7000},
    {'host': '10.1.162.38', 'port': 7001},
])

# logging config
PROCESSNAME = sys.argv[1]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'bjfuzj': {
            'format': '%(asctime)s %(levelname)s [FILENAME: %(pathname)s FUNC: %(funcName)s] [MSG: %(message)s]'
        }
    },
    'handlers': {
        'bjfuzj': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'bjfuzj',
            'filename': '/var/log/aim/cloudwise/fingw/%s.log' % PROCESSNAME,
            'when': 'midnight',
            'backupCount': 3
        }
    },
    'loggers': {
        'bjfuzj': {
            'handlers': ['bjfuzj'],
            'propagate': False,
            'level': 'INFO'
        },
        'elasticsearch': {
            'handlers': ['bjfuzj'],
            'propagate': False,
            'level': 'INFO'
        },
    }
}
logging.config.dictConfig(LOGGING)
bxLogger = logging.getLogger('bjfuzj')


def sigHandler(signum, frame):
    bxLogger.info("收到系统信号: %d, 关闭消费循环" % signum)
    # 因为是通过开多线程进行的信号绑定，所以需要指定修改全局变量
    global RUNNING
    RUNNING = False

def logCommit(err, partitions):
    if err:
        bxLogger.error('commit发生异常: %s' % str(err))
    else:
        bxLogger.info('在partition[%s]执行commit成功' % str(partitions))

def doSG_v3(msg):
    retF = None
    try:
        tmp = json.loads(msg)
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

            retF = ret
            # # UTC timezone to local
            # timestamp = datetime.datetime.strptime(ret['@timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours = 8)
            # index = "reaim-%s" % datetime.datetime.strftime(timestamp, '%Y.%m.%d')
            # ret['@timestamp'] = datetime.datetime.strftime(timestamp, '%s%f')[:13]
            # ES.index(index = index, doc_type = 'trans', body = ret)
        else:
            RD.expire(k, EXPIRE)
        
    except KeyError:
        bxLogger.error(json.dumps(tmp))
        
    except Exception:
        bxLogger.error(traceback.format_exc())

    finally:
        return retF
        

def bulkToES(message):
    bxLogger.info('开始bulk提交ES')
    try:
        timestamp = datetime.datetime.strptime(message[1]['@timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours = 8)
        # 为了提高效率，可以忍受少部分非当天数据进入当天的index
        index = "reaim-%s" % datetime.datetime.strftime(timestamp, '%Y.%m.%d')
        ES.bulk(index = index, doc_type = 'trans', body = message)
        bxLogger.info('提交ES成功')
    except Exception:
        bxLogger.error('提交ES发生异常: ' + traceback.format_exc())

    
def main():
    bxLogger.info("启动交易监控二次加工, 编号: %s" % PROCESSNAME)
    signal.signal(15, sigHandler)
    KAFKAS = {
        'bootstrap.servers': '10.1.160.19:19092,10.1.161.18:19092,10.1.162.38:19092', 
        'group.id': 'reAIM',
        'on_commit': logCommit
    }
    TOPIC = ['fingw']

    c = Consumer(KAFKAS)

    c.subscribe(TOPIC)
    # 使用bulk提交，减少ES压力
    BULKS = []
    # 每100笔提交一次，因为有index，所以*2
    BULKCOUNT = 200
    while RUNNING:
        msg = c.poll(timeout = 1.0)
        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # bxLogger.warn('Topic: %s, Partition: %s 已消费到最新offset: %d' % (msg.topic(), msg.partition(), msg.offset()))
                pass
            else:
                bxLogger.error('发生未知异常: %s', msg.error())

        else:
            ret = doSG_v3(msg.value())
            # {'index': {}}
            if ret is not None:
                BULKS.append({'index': {}})
                BULKS.append(ret)
                if len(BULKS) == BULKCOUNT:
                    # bxLogger.info(BULKS)
                    bulkToES(BULKS)
                    # reInit
                    BULKS = []

    try:
        c.close()
        bxLogger.info('退出消费, 并将剩余数据统一提交ES')
        if len(BULKS) > 0:
            bulkToES(BULKS)
    except Exception:
        bxLogger.error('退出消费发生异常: ' + traceback.format_exc())

    
if __name__ == '__main__':
    main()

