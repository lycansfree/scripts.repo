#!/bin/bash --login

basedir=$(cd `dirname $0`;pwd)
bakdir="${basedir}/bakapp"

# 打印方法改进，方便控制不同的字符类型
print_format() {
    local message
    message=$1
    echo "${message}"
}

# cd命令必须检查，防止因权限/不存在等问题导致切换到错误目录
check_cd() {
    local _dir_
    _dir_=$1
    cd "${_dir_}"
    if [ $? != 0 ];then
        print_format "目标路径${_dir_}不存在或没有读取权限"
        exit 3
    fi
}

# 部署脚本版本号
print_format "部署脚本版本号 = v3.2.1"
print_format "本次升级改动:添加platform参数,针对非tomcat/jboss的,传入启动停止命令,否则手动编写startup.sh不利于迁移"

# bindir必须是绝对路径
# 获取命令行参数
while [ $# -gt 0 ]
do
    case "$1" in
        -plf)
            # platform不可为空
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "platform不可为空"
                exit 1
            else
                _contain=$1
            fi
            ;;
        -app)
            # appdir不可为空
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "appdir不可为空"
                exit 1
            else
                appdir=$1
            fi
            ;;
        -bin)
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "bindir不可为空"
                exit 1
            else
                bindir=$1
            fi
            ;;
        -tmp)
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "tmpdir不可为空"
                exit 1
            else
                tmpdir=$1
            fi
            ;;
        -port)
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "主端口号不可为空"
                exit 1
            else
                _port=$1
            fi
            ;;
        -url)
            shift
            if [ "${1:0:1}" == "-" ];then
                # url可以为空
                continue
            else
                _url=$1
            fi
            ;;
        -version)
            shift
            if [ "${1:0:1}" == "-" ];then
                # version可以为空
                continue
            else
                _version=$1
            fi
            ;;
        -start)
            shift
            if [ "${1:0:1}" == "-" ];then
                # startshell可以为空
                continue
            else
                startshell=$1
            fi
            ;;
        -stop)
            shift
            if [ "${1:0:1}" == "-" ];then
                # stopshell可以为空
                continue
            else
                stopshell=$1
            fi
            ;;
        -file)
            shift
            if [ "${1:0:1}" == "-" ];then
                # filename可以为空
                continue
            else
                filename=$1
                # prefix=${filename%%.*}
                # suffix=${filename##*.}
            fi
            ;;
        -main)
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "模式不可为空"
                exit 1
            else
                _main=$1
            fi
            ;;
        -exit)
            # 该选项用于脚本命令行参数的最后一个，是防止不可为空的校验不准确
            print_format "命令行参数获取完成，进入校验阶段..."
            break
            ;;
        *)
            print_format "$1是未知参数"
            exit 3
            ;;
    esac
    shift
done

check_env() {
    print_format "开始校验部署环境..."
    # 先检查是否Linux环境
    if [ `uname` != "Linux" ];then
        print_format "请在Linux环境下运行"
        exit 3
    fi

    # 加载环境变量，并进入bindir
    . ~/.bash_profile
    check_cd "${bindir}"
    _user=`stat -c %U ${bindir}`

    _service=${bindir%/*}

    # 判断用户是否匹配
    if [ "${_user}" != `whoami` ];then
        print_format "请使用${_user}执行部署脚本"
        exit 3
    fi

    # 根据平台参数确认启/停命令
    # 当前预置tomcat/jboss命令,如未在数据库中配置,则自动获取
    if [ "${_contain}" == "tomcat" ];then
        #export CATALINA_PID="${bindir}/tomcat.pid"
        pre_startshell="sh catalina.sh start"
        pre_stopshell="sh catalina.sh stop"
    elif [ "${_contain}" == "jboss" ];then
        # 获取jboss-cli的IP/端口/offset
        Jip=`cat "${_service}/standalone/configuration/standalone.xml" | grep "jboss.bind.address.management" | grep -oP "192.168.\d+.\d+"`
        Jport=`cat "${_service}/standalone/configuration/standalone.xml" | grep "jboss.management.native.port" | grep -oP "\d+"`
        Jset=`cat "${_service}/standalone/configuration/standalone.xml" | grep "jboss.socket.binding.port-offset" | grep -oP "\d+"`
        let Jport=${Jport}+${Jset}
        _Jconn="${Jip}:${Jport}"
        pre_startshell="sh standalone.sh 1>/dev/null 2>&1 &"
        pre_stopshell="sh jboss-cli.sh --connect controller=${_Jconn} --command=:shutdown"
    fi

    if [ -z "${startshell}" ];then
        startshell=${pre_startshell}
    fi

    if [ -z "${stopshell}" ];then
        stopshell=${pre_stopshell}
    fi

    if [ "${_contain}" != "ics" ];then
        if [ -z "${startshell}" -o -z "${stopshell}" ];then
            print_format "请配置启动/停止命令"
            exit 1
        fi
    fi

    # 判断模式(_main)和所填入参数是否匹配
    for file in ${filename//,/ }
    do
        suffix=${file##*.}
        case "${_main}" in
            deploy)
                if [ "${suffix}" != "war" -a "${suffix}" != "zip" -a "${suffix}" != "tgz" ];then
                    print_format "部署模式只支持.war/zip/tgz格式的归档文件"
                    exit 2
                fi
                ;;
            rollback)
                if [ "${_contain}" != "ics" -a "${suffix}" != "gz" ];then
                    print_format "非ics平台回滚模式只支持.gz格式的归档文件"
                    exit 2
                fi

                if [ -z "${_version}" ];then
                    print_format "回滚模式需要提供版本号"
                    exit 2
                fi

                if [ ! -d "${bakdir}/${_version}" ];then
                    print_format "${_version}版本号不存在"
                    exit 2
                fi
                ;;
        esac
    done

    print_format "环境校验通过"
    echo ""
}

get_pid() {
    # ps 获取,注意需要加上grep java
    _pid=`ps -fu ${_user} | grep java | grep -w ${_service} | grep -vE "grep|$0" | awk '{print $2}'`

    # _chpid用来检查_pid是否唯一，只要wc -l为1，就将值赋给pid(无论是否为空)
    _chpid=`echo "${_pid}" | xargs -n 1 | wc -l`
    if [ ${_chpid} == 1 ];then
        pid=${_pid}
    else
        print_format "进程不唯一，无法获取有效的pid值，请检查后再执行部署脚本"
        exit 2
    fi
}

file_exist() {
    # 检查待部署或待回退的包是否存在
    print_format "开始文件列表校验..."
    mkdir -p "${bakdir}"
    case "${_main}" in
        deploy)
            _count=0
            for file in ${filename//,/ }
            do
                if [ ! -f "${tmpdir}/${file}" ];then
                    print_format "${file}不存在,请检查"
                    exit 1
                fi
                let _count=${_count}+1
            done

            if [ "${_contain}" == "ics" -a "${_count}" -gt 1 ];then
                print_format "ICS平台仅支持单文件部署"
            else
                print_format "本次部署${_count}个文件"
            fi
            ;;
        rollback)
            if [ "${_contain}" == "ics" ];then
                for rollFile in `cat ${bakdir}/${_version}/update.list`
                do
                    if [ ! -f "${bakdir}/${_version}/${rollFile}" ];then
                        print_format "${rollFile}不存在,请检查"
                        exit 1
                    fi
                done
            else
                for file in ${filename//,/ }
                do
                    if [ ! -f "${bakdir}/${_version}/${file}" ];then
                        print_format "${file}不存在,请检查"
                        exit 1
                    fi
                done
            fi
            ;;
    esac

    print_format "${filename//,/ }准备就绪"
    echo ""
}

check_port() {
    # 检查端口的监听情况
    for i in `seq 10`
    do
        netstat -lnt | awk '{print $4}' | grep -E ":${_port}$" 1>/dev/null 2>&1
        if [ $? == 0 ];then
            print_format "${_port}端口监听 = 成功"
            break
        else
            if [ ${i} == 10 ];then
                print_format "${_port}端口监听 = 失败"
            fi
        fi
        sleep 1
    done
    

    # 检查url是否可以正常调用，可选，根据_url是否为空
    # 获取的http_code以2或3开头即正常，其余为不正常
    if [ -z "${_url}" ];then
        print_format "url为空，跳过检查"
    else
        for i in `seq 10`
        do
            http_code=`curl -m 2 -o /dev/null -s -w %{http_code} ${_url}`
            if [ ${http_code:0:1} == 2 -o ${http_code:0:1} == 3 ];then
                print_format "${_url} = 校验成功(${http_code})"
                break
            else
                if [ ${i} == 10 ];then
                    print_format "${_url} = 校验失败(${http_code})"
                fi
            fi
            sleep 1
        done
    fi
}

startApp() {
    # 启动应用
    print_format "开始启动..."
    check_cd "${bindir}"
    eval "${startshell}"

    sleep 2
    print_format "准备启动后检查"
    echo ""
}

killApp() {
    # 检查进程,timeout后直接kill
    _timeout=10
    for i in `seq ${_timeout}`
    do
        ps -p ${pid} 1>/dev/null 2>&1
        if [ $? == 0 ];then
            # 最后一次检查仍不成功的，kill
            if [ ${i} == ${_timeout} ];then
                kill -9 ${pid}
                print_format "服务(pid=${pid})未在${_timeout}秒内停止成功,KILL"
            fi
        else
            print_format "服务(pid=${pid})使用shutdown停止成功"
            break
        fi
        sleep 1
    done
}

stopApp() {
    # 停止应用
    get_pid
    printf "开始停止..."
    eval "${stopshell}"
    killApp
    # 暂停一秒保证停止成功
    sleep 1
    echo ""
}

deployApp() {
    # 部署应用
    print_format "开始部署..."
    for file in ${filename//,/ }
    do
        _mode_=`echo "${_mode}" | xargs -n 2 | grep -w ${file} | awk '{print $2}'`
        if [ ${_mode_} == "_up_" ];then
            print_format "${file}部署模式 == uncompress"
            suxFile=${file##*.}
            # 解压分2种包,war和zip用unzip,tgz用tar
            case "${suxFile}" in
                war)
                    unzip -od ${appdir} ${tmpdir}/${file} 1>/dev/null 2>&1
                    ;;
                zip)                    
                    unzip -od ${appdir} ${tmpdir}/${file} 1>/dev/null 2>&1
                    ;;
                tgz)
                    tar -zxf ${tmpdir}/${file} -C ${appdir}
                    ;;
            esac
        elif [ ${_mode_} == "_cp_" ];then
            print_format "${file}部署模式 == copy"
            # 拷贝
            cp ${tmpdir}/${file} ${appdir}
        fi
    done
    print_format "部署完成"
    echo ""
}

rollbackApp() {
    # 回退应用
    print_format "开始回退..."
    check_cd "${appdir}"
    for file in ${filename//,/ }
    do
        # 只回退tar.gz包中有的内容
        listFile=`tar -ztf ${bakdir}/${_version}/${file} | awk -F "/" '{print $1}' | sort | uniq`

        # 删除listFile
        print_format "回退删除 = ${listFile}"
        /bin/rm -rf ${listFile}

        # 将备份的版本取回并部署
        print_format "回退版本 = ${bakdir}/${_version}/${file}"
        tar -zxf ${bakdir}/${_version}/${file} -C ${appdir}
    done
    print_format "回退完成"
    echo ""
}

bakApp() {
    # 备份应用
    # 创建备份目录名称
    print_format "开始备份..."
    check_cd "${bakdir}"
    _today=`date +'%Y%m%d'`
    _release=`ls -d ${_today}* 2>/dev/null | wc -l`
    _version="${_today}_${_release}"
    mkdir -p "${bakdir}/${_today}_${_release}"
    print_format "备份版本 = ${_today}_${_release}"

    for file in ${filename//,/ }
    do
        # 去掉后缀的.war或.zip,然后查找是否含有file或preFile
        # 若有则只备份file和preFile
        # 若无，则备份全部，除link文件
        # 备份方法，先mv到备份路径(这么做是为了防止直接rm)，然后打包
        check_cd "${appdir}"
        # 取前缀只要删除一个.*
        preFile=${file%.*}
        suxFile=${file##*.}
        _mode=""
        case "${suxFile}" in
            war)
                # 只有war包不解压和回退可能出现多个包部署
                numFile=`ls -d ${file} ${preFile} 2>/dev/null | wc -l`
                if [ ${numFile} == 0 ];then
                    # 为0则解压,需要根据包中的文件得到listFile
                    listFile=`unzip -l ${bakdir}/${file} | awk '{if($1~/^[0-9].*/) print $4}' | awk -F "/" '{print $1}' | sort | uniq | xargs`
                    _mode="${file} _up_ ${_mode}"
                else
                    listFile=`ls -d ${file} ${preFile} 2>/dev/null | xargs`
                    _mode="${file} _cp_ ${_mode}"
                fi
                mv ${listFile} "${bakdir}/${_today}_${_release}"
                if [ $? -gt 0 ];then
                    echo "#####################################"
                    print_format "备份异常,此时可能为新增文件,也可能是appdir配置错误,请注意核实"
                    echo "#####################################"
                fi
                ;;
            zip)
                # 增量不需要删除,故只备份,同时增量需要解压
                _mode="${file} _up_ ${_mode}"
                listFile=`unzip -l ${bakdir}/${file} | awk '{if($1~/^[0-9].*/) print $4}' | awk -F "/" '{print $1}' | sort | uniq | xargs`
                cp -r ${listFile} "${bakdir}/${_today}_${_release}"
                if [ $? -gt 0 ];then
                    echo "#####################################"
                    print_format "备份异常,此时可能为新增文件,也可能是appdir配置错误,请注意核实"
                    echo "#####################################"
                fi
                ;;
            tgz)
                # dubbo/dsf等项目，直接打tgz包
                _mode="${file} _up_ ${_mode}"
                listFile=`tar -ztf ${bakdir}/${file} | awk -F "/" '{print $1}' | sort | uniq | xargs`
                mv ${listFile} "${bakdir}/${_today}_${_release}"
                if [ $? -gt 0 ];then
                    echo "#####################################"
                    print_format "备份异常,此时可能为新增文件,也可能是appdir配置错误,请注意核实"
                    echo "#####################################"
                fi
                ;;
        esac
        check_cd "${bakdir}/${_today}_${_release}"
        tar -zcf ${preFile}.tar.gz ${listFile}
        /bin/rm -rf ${listFile}

        # 打印备份信息
        print_format "备份包名 = ${preFile}.tar.gz"
    done
    print_format "备份完成"
    echo ""
}


hsbakApp() {
    # ICS项目备份
    print_format "开始ICS备份..."
    check_cd "${bakdir}"
    _today=`date +'%Y%m%d'`
    _release=`ls -d ${_today}* 2>/dev/null | wc -l`
    _version="${_today}_${_release}"
    mkdir -p "${bakdir}/${_today}_${_release}"
    print_format "备份版本 = ${_today}_${_release}"

    check_cd ${appdir}
    # 初始化2个记录文件,防止有错误记录
    _update="${bakdir}/${_version}/update.list"
    _insert="${bakdir}/${_version}/insert.list"
    cat /dev/null > ${_update}
    cat /dev/null > ${_insert}

    for bakfile in `/usr/bin/unzip -l ${tmpdir}/${filename} | awk '{if($1 ~ "^[1-9]") print $4}'`
    do
        if [ -f ${bakfile} ];then
            echo "${bakfile}" >> ${_update}
            mkdir -p ${bakdir}/${_version}/${bakfile%/*}
            mv ${bakfile} ${bakdir}/${_version}/${bakfile}
        else
            echo "${bakfile}" >> ${_insert}
        fi
    done

    # 将2个文件置为只读,防止误操作篡改
    chmod 400 ${_update}
    chmod 400 ${_insert}

    print_format "备份完成"
    echo "#####################################"
    print_format "本次更新文件列表如下:"
    cat ${_update}
    print_format "本次新增文件列表如下:"
    cat ${_insert}
    echo "#####################################"
    echo ""
}

hsrollbackApp() {
    # ICS项目回退
    print_format "开始ICS回滚..."
    check_cd ${appdir}
    for rollFile in `cat ${bakdir}/${_version}/insert.list`
    do
        # 上次新增的文件删除之
        /bin/rm -f ${rollFile}
    done

    for rollFile in `cat ${bakdir}/${_version}/update.list`
    do
        # 上次更新的文件替换之
        cp ${bakdir}/${_version}/${rollFile} ${rollFile}
    done
    print_format "已回滚到${_version}版本"
}

hsdeployApp() {
    # ICS项目部署
    print_format "开始ICS部署..."
    local _error_ _status_
    _error_=`/usr/bin/unzip -od ${appdir} ${tmpdir}/${filename} 2>&1 1>/dev/null`
    _status_=$?

    if [ ${_status_} != 0 ];then
        print_format "部署失败,详细信息如下:"
        print_format "${_error_}"
        exit 2
    else
        print_format "代码部署完成"
    fi
}




#### 入口 ####

# 第一步校验
check_env


case "${_main}" in
    deploy)
        file_exist
        if [ "${_contain}" == "ics" ];then
            hsbakApp
            hsdeployApp
        else
            stopApp
            bakApp
            deployApp
            startApp
            check_port
        fi
        ;;
    rollback)
        file_exist
        if [ "${_contain}" == "ics" ];then
            hsrollbackApp
        else
            stopApp
            rollbackApp
            startApp
            check_port
        fi
        ;;
    restart)
        stopApp
        startApp
        check_port
        ;;
    start)
        startApp
        check_port
        ;;
    stop)
        stopApp
        ;;
    *)
        print_format "${_main}是未知模式"
        exit 3
        ;;
esac

