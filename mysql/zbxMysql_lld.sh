#!/bin/bash

# zabbix mysql port lld
 
for port in `netstat -lntp 2>/dev/null | grep "mysqld" | awk '{print $4}' | awk -F ":" '{print $NF}' | sort | uniq`
do
    if [ -z "${output}" ];then
        output="{\"{#MYSQLPORT}\":\"${port}\"}"
    else
        output="${output},{\"{#MYSQLPORT}\":\"${port}\"}"
    fi
done
 
echo "{\"data\":[${output}]}" | python -m json.tool

