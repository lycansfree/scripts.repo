#!/usr/bin/env python
# coding:utf-8

import json
import yaml
import os,sys

def main():
    conf = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])),'zbxLog.yml')
    output = {"data":[]}
    with open(conf,'r') as f:
        config = yaml.load(f.read().decode('gbk'))

    logIDs = config["logIDs"]
    for id in logIDs:
        output["data"].append({"{#LOGKEY}":str(id),"{#LOGNAME}":config[id]["logname"].encode('UTF-8')})

    print json.dumps(output,indent = 4,ensure_ascii = False)

if __name__ == '__main__':
    main()

