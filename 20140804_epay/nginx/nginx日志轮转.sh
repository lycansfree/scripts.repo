#!/bin/bash

# 按天轮转nginx日志(自动识别所有当前日志)
# 脚本放置在logs路径下

. ~/.bash_profile
currDir=$(cd `dirname $0`;pwd)
binDir="${currDir}/../sbin"
archDir="${currDir}/archlog"

yesterday=`date -d "-1 days" +%Y%m%d`
mkdir -p ${archDir}

reload_flag=0
for name in `ls *.log 2>/dev/null`
do
    if [ ! -f ${archDir}/${name}.${yesterday} ];then
        mv ${name} ${archDir}/${name}.${yesterday}
        reload_flag=1
    fi
done

if [ ${reload_flag} == 1 ];then
    ${binDir}/nginx -s reload
fi

