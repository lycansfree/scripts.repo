#!/bin/bash

# mysql5.6自定义启动脚本

basedir=$(cd `dirname $0`;pwd)
conf="${basedir%/*}/conf/my.cnf"
pidfile=`cat ${conf} | grep "pid-file" | awk -F "=" '{print $2}'`
socketfile=`cat ${conf} | grep "socket" | awk -F "=" '{print $2}'`

TIMEOUT=60

# functions
. /etc/rc.d/init.d/functions

print_color() {
    content=$1
    color=$2
    case $2 in
        yellow)
        color_code="\e[0;33;1m"
        ;;
        red)
        color_code="\e[0;31;1m"
        ;;
        green)
        color_code="\e[0;32;1m"
        ;;
    esac
    echo -e "${color_code}${content}\e[0m"
}

startApp() {
    statusApp
    if [ $? == 2 ];then
        /bin/sh /usr/bin/mysqld_safe --defaults-file=${conf} 1>/dev/null 2>&1 &
        for i in `seq ${TIMEOUT}`
        do
            statusApp
            ret=$?
            if [ ${ret} == 0 ];then
                action "mysql[${pid}] start" /bin/true
                break
            fi
        done

        if [ ${i} == ${TIMEOUT} -a ${ret} -gt 0 ];then
            action "mysql start timeout" /bin/false
            exit 2
        fi
    else
        print_color "mysql already running" yellow
    fi
}

stopApp() {
    statusApp
    if [ $? == 2 ];then
        print_color "mysql already stopped" red
    else
        # statusApp already get the pid value
        kill ${pid} 1>/dev/null 2>&1
        for i in `seq ${TIMEOUT}`
        do
            statusApp
            ret=$?
            if [ ${ret} == 2 ];then
                action "mysql[${pid}] stop" /bin/true
                break
            fi
        done

        if [ ${i} == ${TIMEOUT} -a ${ret} -lt 2 ];then
            action "mysql[${pid}] stop timeout" /bin/false
            exit 2
        fi
    fi
}

statusApp() {
    sleep 1
    if [ -f ${pidfile} ];then
        pid=`cat ${pidfile}`
        ps -p ${pid} 1>/dev/null 2>&1
        if [ $? == 0 ];then
            # process start,check service
            /usr/bin/mysqladmin -S ${socketfile} -u UNKNOWN_MYSQL_USER ping 1>/dev/null 2>&1
            if [ $? == 0 ];then
                # service running
                return 0
            else
                # service failed
                return 1
            fi
        else
            # not running but the file exist
            rm -f ${pidfile}
            return 2
        fi
    else
        # not running
        return 2
    fi
}

case "$1" in
    start)
        startApp
        ;;
    stop)
        stopApp
        ;;
    restart | reload)
        stopApp
        startApp
        ;;
    status)
        statusApp
        ret=$?
        case "${ret}" in
            0)
            print_color "mysql[${pid}] running" green
            ;;
            1)
            print_color "mysql[${pid}] out of service" yellow
            ;;
            2)
            print_color "mysql stopped" red
            ;;
        esac
        ;;
    *)
        print_color "sh $0 [start|stop|restart|status]" red
        ;;
esac


