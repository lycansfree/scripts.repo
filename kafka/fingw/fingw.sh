#!/bin/bash

workdir=$(cd `dirname $0`;pwd)
keyword="consumer_fingw_reaim"
CONSUMER="${workdir}/${keyword}.py"
NUM=2
user="sherlock"
WAITSEC=60


pidcheck() {
    # return 0 => 正常
    # return 1 => 已停止
    # return 2 => 其它异常
    local pid=$1
    kill -0 ${pid} 1>/dev/null 2>&1
    if [ $? == 0 ];then
        # piduser=`ps -p ${pid} -o user | tail -1`
        # if [ "${piduser}" != "${user}" ];then
        #     ret
        # fi

        ps -p ${pid} -o command | grep "${keyword}" 1>/dev/null 2>&1
        if [ $? == 0 ];then
            return 0
        else
            return 1
        fi

    else
        return 1
    fi
}

statusApp() {
    for x in `seq ${NUM}`
    do
        pidFile="${workdir}/.fingw${x}.pid"
        pidcheck `cat ${pidFile}`
        if [ $? == 1 ];then
            startApp "fingw.${x}" ${pidFile}
        fi
    done
}

startApp() {
    local procArg=$1
    local pidFile=$2
    ${CONSUMER} ${procArg} 1>/dev/null 2>&1 &
    echo $! > ${pidFile}
}

stopApp() {
    local pid
    for x in `seq ${NUM}`
    do
        pidFile="${workdir}/.fingw${x}.pid"
        pid=`cat ${pidFile}`
        pidcheck ${pid}
        if [ $? == 1 ];then
            continue
        fi

        kill ${pid}
        for y in `seq ${WAITSEC}`
        do
            pidcheck ${pid}
            if [ $? == 1 ];then
                break
            fi

            if [ ${y} == ${WAITSEC} ];then
                kill -9 ${pid}
            fi
        done
    done
}

loopApp() {
    while true
    do
        statusApp
        sleep ${WAITSEC}
    done
}

case "$1" in
    start)
        statusApp
        ;;
    stop)
        stopApp
        ;;
    restart)
        stopApp
        statusApp
        ;;
    loop)
        loopApp
        ;;
    *)
        echo "$0 start | stop | loop"
        exit 2
        ;;
esac

