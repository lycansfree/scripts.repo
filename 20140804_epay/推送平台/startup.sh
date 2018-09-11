#!/bin/bash

. ~/.bash_profile

CWD=$(cd `dirname $0`;pwd)
pidFile="${CWD}/running/main.pid"

startApp() {
    # 启动
    statusApp
    s=$?
    if [ ${s} == 0 ];then
        echo "please do not startup repetitive!!!"
    else
        nohup ${CWD}/trans_worker.py 1>/dev/null 2>&1 &
        sleep 2
        statusApp
    fi
}

stopApp() {
    # 停止
    statusApp
    s=$?
    if [ ${s} == 0 ];then
        kill -9 ${pid}
        sleep 2
        statusApp
    fi
}

statusApp() {
    # 状态
    if [ -f ${pidFile} ];then
        pid=`cat ${pidFile}`
        kill -0 ${pid} 2>/dev/null
        if [ $? == 0 ];then
            ss=0
            echo "trans_worker is running"
        else
            ss=1
            echo "trans_worker stopped"
        fi
    else
        ss=2
        echo "${pidFile} disappeared"
    fi
    return ${ss}
}

case "$1" in
    start)
        startApp
        ;;
    stop)
        stopApp
        ;;
    restart)
        stopApp
        startApp
        ;;
    status)
        statusApp
        ;;
    *)
        echo "sh $0 [start|stop|restart|status]"
        exit 2
esac

