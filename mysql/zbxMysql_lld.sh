#!/bin/bash

# 默认第一个是option
# 第二个是阈值
# 其他通过-x的选项来添加
option="${1:-mysqlPortOnly}"
threshold="${2:-80}"

# while [ $# -gt 0 ]
# do
#     case "$1" in
#         -y)
#             shift
#             if [ "${1:0:1}" == "-" ];then
#                 exit 1
#             else
#                 threshold=$1
#             fi
#             ;;
#     esac
#     shift
# done

mysqlPortOnly() {
    for port in `netstat -lntp 2>/dev/null | grep "mysqld" | awk '{print $4}' | awk -F ":" '{print $NF}' | sort | uniq`
    do
        if [ -z "${output}" ];then
            output="{\"{#MYSQLPORT}\":\"${port}\"}"
        else
            output="${output},{\"{#MYSQLPORT}\":\"${port}\"}"
        fi
    done
}

mysqlConnCheck() {
    for port in `netstat -lntp 2>/dev/null | grep "mysqld" | awk '{print $4}' | awk -F ":" '{print $NF}' | sort | uniq`
    do
        # 根据port查看mysql实例配置
        connInit=`/home/mysql/mysql_${port}/bin/mysql --defaults-file=/home/mysql/mysql_${port}/etc/user.root.cnf -A -s -e \
            "select VARIABLE_VALUE from information_schema.GLOBAL_VARIABLES where variable_name = 'max_connections'" 2>/dev/null | tail -1`
        # 计算阈值,默认80%
        conns=`python -c "print ${connInit:-2000} * ${threshold} / 100"`

        if [ -z "${output}" ];then
            output="{\"{#MYSQLPORT}\":\"${port}\",\"{#MYSQLCONNTHS}\":\"${conns}\"}"
        else
            output="${output},{\"{#MYSQLPORT}\":\"${port}\",\"{#MYSQLCONNTHS}\":\"${conns}\"}"
        fi
    done
}

case "${option}" in
    mysqlPortOnly)
        mysqlPortOnly
        ;;
    mysqlConnCheck)
        mysqlConnCheck
        ;;
esac
 
echo "{\"data\":[${output}]}" | python -m json.tool

