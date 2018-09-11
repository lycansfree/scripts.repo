#!/bin/bash --login

basedir=$(cd `dirname $0`;pwd)
bakdir="${basedir}/bakapp"

# ��ӡ�����Ľ���������Ʋ�ͬ���ַ�����
print_format() {
    local message
    message=$1
    echo "${message}"
}

# cd��������飬��ֹ��Ȩ��/�����ڵ����⵼���л�������Ŀ¼
check_cd() {
    local _dir_
    _dir_=$1
    cd "${_dir_}"
    if [ $? != 0 ];then
        print_format "Ŀ��·��${_dir_}�����ڻ�û�ж�ȡȨ��"
        exit 3
    fi
}

# ����ű��汾��
print_format "����ű��汾�� = v3.2.1"
print_format "���������Ķ�:���platform����,��Է�tomcat/jboss��,��������ֹͣ����,�����ֶ���дstartup.sh������Ǩ��"

# bindir�����Ǿ���·��
# ��ȡ�����в���
while [ $# -gt 0 ]
do
    case "$1" in
        -plf)
            # platform����Ϊ��
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "platform����Ϊ��"
                exit 1
            else
                _contain=$1
            fi
            ;;
        -app)
            # appdir����Ϊ��
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "appdir����Ϊ��"
                exit 1
            else
                appdir=$1
            fi
            ;;
        -bin)
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "bindir����Ϊ��"
                exit 1
            else
                bindir=$1
            fi
            ;;
        -tmp)
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "tmpdir����Ϊ��"
                exit 1
            else
                tmpdir=$1
            fi
            ;;
        -port)
            shift
            if [ "${1:0:1}" == "-" ];then
                print_format "���˿ںŲ���Ϊ��"
                exit 1
            else
                _port=$1
            fi
            ;;
        -url)
            shift
            if [ "${1:0:1}" == "-" ];then
                # url����Ϊ��
                continue
            else
                _url=$1
            fi
            ;;
        -version)
            shift
            if [ "${1:0:1}" == "-" ];then
                # version����Ϊ��
                continue
            else
                _version=$1
            fi
            ;;
        -start)
            shift
            if [ "${1:0:1}" == "-" ];then
                # startshell����Ϊ��
                continue
            else
                startshell=$1
            fi
            ;;
        -stop)
            shift
            if [ "${1:0:1}" == "-" ];then
                # stopshell����Ϊ��
                continue
            else
                stopshell=$1
            fi
            ;;
        -file)
            shift
            if [ "${1:0:1}" == "-" ];then
                # filename����Ϊ��
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
                print_format "ģʽ����Ϊ��"
                exit 1
            else
                _main=$1
            fi
            ;;
        -exit)
            # ��ѡ�����ڽű������в��������һ�����Ƿ�ֹ����Ϊ�յ�У�鲻׼ȷ
            print_format "�����в�����ȡ��ɣ�����У��׶�..."
            break
            ;;
        *)
            print_format "$1��δ֪����"
            exit 3
            ;;
    esac
    shift
done

check_env() {
    print_format "��ʼУ�鲿�𻷾�..."
    # �ȼ���Ƿ�Linux����
    if [ `uname` != "Linux" ];then
        print_format "����Linux����������"
        exit 3
    fi

    # ���ػ���������������bindir
    . ~/.bash_profile
    check_cd "${bindir}"
    _user=`stat -c %U ${bindir}`

    _service=${bindir%/*}

    # �ж��û��Ƿ�ƥ��
    if [ "${_user}" != `whoami` ];then
        print_format "��ʹ��${_user}ִ�в���ű�"
        exit 3
    fi

    # ����ƽ̨����ȷ����/ͣ����
    # ��ǰԤ��tomcat/jboss����,��δ�����ݿ�������,���Զ���ȡ
    if [ "${_contain}" == "tomcat" ];then
        #export CATALINA_PID="${bindir}/tomcat.pid"
        pre_startshell="sh catalina.sh start"
        pre_stopshell="sh catalina.sh stop"
    elif [ "${_contain}" == "jboss" ];then
        # ��ȡjboss-cli��IP/�˿�/offset
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
            print_format "����������/ֹͣ����"
            exit 1
        fi
    fi

    # �ж�ģʽ(_main)������������Ƿ�ƥ��
    for file in ${filename//,/ }
    do
        suffix=${file##*.}
        case "${_main}" in
            deploy)
                if [ "${suffix}" != "war" -a "${suffix}" != "zip" -a "${suffix}" != "tgz" ];then
                    print_format "����ģʽֻ֧��.war/zip/tgz��ʽ�Ĺ鵵�ļ�"
                    exit 2
                fi
                ;;
            rollback)
                if [ "${_contain}" != "ics" -a "${suffix}" != "gz" ];then
                    print_format "��icsƽ̨�ع�ģʽֻ֧��.gz��ʽ�Ĺ鵵�ļ�"
                    exit 2
                fi

                if [ -z "${_version}" ];then
                    print_format "�ع�ģʽ��Ҫ�ṩ�汾��"
                    exit 2
                fi

                if [ ! -d "${bakdir}/${_version}" ];then
                    print_format "${_version}�汾�Ų�����"
                    exit 2
                fi
                ;;
        esac
    done

    print_format "����У��ͨ��"
    echo ""
}

get_pid() {
    # ps ��ȡ,ע����Ҫ����grep java
    _pid=`ps -fu ${_user} | grep java | grep -w ${_service} | grep -vE "grep|$0" | awk '{print $2}'`

    # _chpid�������_pid�Ƿ�Ψһ��ֻҪwc -lΪ1���ͽ�ֵ����pid(�����Ƿ�Ϊ��)
    _chpid=`echo "${_pid}" | xargs -n 1 | wc -l`
    if [ ${_chpid} == 1 ];then
        pid=${_pid}
    else
        print_format "���̲�Ψһ���޷���ȡ��Ч��pidֵ���������ִ�в���ű�"
        exit 2
    fi
}

file_exist() {
    # �������������˵İ��Ƿ����
    print_format "��ʼ�ļ��б�У��..."
    mkdir -p "${bakdir}"
    case "${_main}" in
        deploy)
            _count=0
            for file in ${filename//,/ }
            do
                if [ ! -f "${tmpdir}/${file}" ];then
                    print_format "${file}������,����"
                    exit 1
                fi
                let _count=${_count}+1
            done

            if [ "${_contain}" == "ics" -a "${_count}" -gt 1 ];then
                print_format "ICSƽ̨��֧�ֵ��ļ�����"
            else
                print_format "���β���${_count}���ļ�"
            fi
            ;;
        rollback)
            if [ "${_contain}" == "ics" ];then
                for rollFile in `cat ${bakdir}/${_version}/update.list`
                do
                    if [ ! -f "${bakdir}/${_version}/${rollFile}" ];then
                        print_format "${rollFile}������,����"
                        exit 1
                    fi
                done
            else
                for file in ${filename//,/ }
                do
                    if [ ! -f "${bakdir}/${_version}/${file}" ];then
                        print_format "${file}������,����"
                        exit 1
                    fi
                done
            fi
            ;;
    esac

    print_format "${filename//,/ }׼������"
    echo ""
}

check_port() {
    # ���˿ڵļ������
    for i in `seq 10`
    do
        netstat -lnt | awk '{print $4}' | grep -E ":${_port}$" 1>/dev/null 2>&1
        if [ $? == 0 ];then
            print_format "${_port}�˿ڼ��� = �ɹ�"
            break
        else
            if [ ${i} == 10 ];then
                print_format "${_port}�˿ڼ��� = ʧ��"
            fi
        fi
        sleep 1
    done
    

    # ���url�Ƿ�����������ã���ѡ������_url�Ƿ�Ϊ��
    # ��ȡ��http_code��2��3��ͷ������������Ϊ������
    if [ -z "${_url}" ];then
        print_format "urlΪ�գ��������"
    else
        for i in `seq 10`
        do
            http_code=`curl -m 2 -o /dev/null -s -w %{http_code} ${_url}`
            if [ ${http_code:0:1} == 2 -o ${http_code:0:1} == 3 ];then
                print_format "${_url} = У��ɹ�(${http_code})"
                break
            else
                if [ ${i} == 10 ];then
                    print_format "${_url} = У��ʧ��(${http_code})"
                fi
            fi
            sleep 1
        done
    fi
}

startApp() {
    # ����Ӧ��
    print_format "��ʼ����..."
    check_cd "${bindir}"
    eval "${startshell}"

    sleep 2
    print_format "׼����������"
    echo ""
}

killApp() {
    # ������,timeout��ֱ��kill
    _timeout=10
    for i in `seq ${_timeout}`
    do
        ps -p ${pid} 1>/dev/null 2>&1
        if [ $? == 0 ];then
            # ���һ�μ���Բ��ɹ��ģ�kill
            if [ ${i} == ${_timeout} ];then
                kill -9 ${pid}
                print_format "����(pid=${pid})δ��${_timeout}����ֹͣ�ɹ�,KILL"
            fi
        else
            print_format "����(pid=${pid})ʹ��shutdownֹͣ�ɹ�"
            break
        fi
        sleep 1
    done
}

stopApp() {
    # ֹͣӦ��
    get_pid
    printf "��ʼֹͣ..."
    eval "${stopshell}"
    killApp
    # ��ͣһ�뱣ֹ֤ͣ�ɹ�
    sleep 1
    echo ""
}

deployApp() {
    # ����Ӧ��
    print_format "��ʼ����..."
    for file in ${filename//,/ }
    do
        _mode_=`echo "${_mode}" | xargs -n 2 | grep -w ${file} | awk '{print $2}'`
        if [ ${_mode_} == "_up_" ];then
            print_format "${file}����ģʽ == uncompress"
            suxFile=${file##*.}
            # ��ѹ��2�ְ�,war��zip��unzip,tgz��tar
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
            print_format "${file}����ģʽ == copy"
            # ����
            cp ${tmpdir}/${file} ${appdir}
        fi
    done
    print_format "�������"
    echo ""
}

rollbackApp() {
    # ����Ӧ��
    print_format "��ʼ����..."
    check_cd "${appdir}"
    for file in ${filename//,/ }
    do
        # ֻ����tar.gz�����е�����
        listFile=`tar -ztf ${bakdir}/${_version}/${file} | awk -F "/" '{print $1}' | sort | uniq`

        # ɾ��listFile
        print_format "����ɾ�� = ${listFile}"
        /bin/rm -rf ${listFile}

        # �����ݵİ汾ȡ�ز�����
        print_format "���˰汾 = ${bakdir}/${_version}/${file}"
        tar -zxf ${bakdir}/${_version}/${file} -C ${appdir}
    done
    print_format "�������"
    echo ""
}

bakApp() {
    # ����Ӧ��
    # ��������Ŀ¼����
    print_format "��ʼ����..."
    check_cd "${bakdir}"
    _today=`date +'%Y%m%d'`
    _release=`ls -d ${_today}* 2>/dev/null | wc -l`
    _version="${_today}_${_release}"
    mkdir -p "${bakdir}/${_today}_${_release}"
    print_format "���ݰ汾 = ${_today}_${_release}"

    for file in ${filename//,/ }
    do
        # ȥ����׺��.war��.zip,Ȼ������Ƿ���file��preFile
        # ������ֻ����file��preFile
        # ���ޣ��򱸷�ȫ������link�ļ�
        # ���ݷ�������mv������·��(��ô����Ϊ�˷�ֱֹ��rm)��Ȼ����
        check_cd "${appdir}"
        # ȡǰ׺ֻҪɾ��һ��.*
        preFile=${file%.*}
        suxFile=${file##*.}
        _mode=""
        case "${suxFile}" in
            war)
                # ֻ��war������ѹ�ͻ��˿��ܳ��ֶ��������
                numFile=`ls -d ${file} ${preFile} 2>/dev/null | wc -l`
                if [ ${numFile} == 0 ];then
                    # Ϊ0���ѹ,��Ҫ���ݰ��е��ļ��õ�listFile
                    listFile=`unzip -l ${bakdir}/${file} | awk '{if($1~/^[0-9].*/) print $4}' | awk -F "/" '{print $1}' | sort | uniq | xargs`
                    _mode="${file} _up_ ${_mode}"
                else
                    listFile=`ls -d ${file} ${preFile} 2>/dev/null | xargs`
                    _mode="${file} _cp_ ${_mode}"
                fi
                mv ${listFile} "${bakdir}/${_today}_${_release}"
                if [ $? -gt 0 ];then
                    echo "#####################################"
                    print_format "�����쳣,��ʱ����Ϊ�����ļ�,Ҳ������appdir���ô���,��ע���ʵ"
                    echo "#####################################"
                fi
                ;;
            zip)
                # ��������Ҫɾ��,��ֻ����,ͬʱ������Ҫ��ѹ
                _mode="${file} _up_ ${_mode}"
                listFile=`unzip -l ${bakdir}/${file} | awk '{if($1~/^[0-9].*/) print $4}' | awk -F "/" '{print $1}' | sort | uniq | xargs`
                cp -r ${listFile} "${bakdir}/${_today}_${_release}"
                if [ $? -gt 0 ];then
                    echo "#####################################"
                    print_format "�����쳣,��ʱ����Ϊ�����ļ�,Ҳ������appdir���ô���,��ע���ʵ"
                    echo "#####################################"
                fi
                ;;
            tgz)
                # dubbo/dsf����Ŀ��ֱ�Ӵ�tgz��
                _mode="${file} _up_ ${_mode}"
                listFile=`tar -ztf ${bakdir}/${file} | awk -F "/" '{print $1}' | sort | uniq | xargs`
                mv ${listFile} "${bakdir}/${_today}_${_release}"
                if [ $? -gt 0 ];then
                    echo "#####################################"
                    print_format "�����쳣,��ʱ����Ϊ�����ļ�,Ҳ������appdir���ô���,��ע���ʵ"
                    echo "#####################################"
                fi
                ;;
        esac
        check_cd "${bakdir}/${_today}_${_release}"
        tar -zcf ${preFile}.tar.gz ${listFile}
        /bin/rm -rf ${listFile}

        # ��ӡ������Ϣ
        print_format "���ݰ��� = ${preFile}.tar.gz"
    done
    print_format "�������"
    echo ""
}


hsbakApp() {
    # ICS��Ŀ����
    print_format "��ʼICS����..."
    check_cd "${bakdir}"
    _today=`date +'%Y%m%d'`
    _release=`ls -d ${_today}* 2>/dev/null | wc -l`
    _version="${_today}_${_release}"
    mkdir -p "${bakdir}/${_today}_${_release}"
    print_format "���ݰ汾 = ${_today}_${_release}"

    check_cd ${appdir}
    # ��ʼ��2����¼�ļ�,��ֹ�д����¼
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

    # ��2���ļ���Ϊֻ��,��ֹ������۸�
    chmod 400 ${_update}
    chmod 400 ${_insert}

    print_format "�������"
    echo "#####################################"
    print_format "���θ����ļ��б�����:"
    cat ${_update}
    print_format "���������ļ��б�����:"
    cat ${_insert}
    echo "#####################################"
    echo ""
}

hsrollbackApp() {
    # ICS��Ŀ����
    print_format "��ʼICS�ع�..."
    check_cd ${appdir}
    for rollFile in `cat ${bakdir}/${_version}/insert.list`
    do
        # �ϴ��������ļ�ɾ��֮
        /bin/rm -f ${rollFile}
    done

    for rollFile in `cat ${bakdir}/${_version}/update.list`
    do
        # �ϴθ��µ��ļ��滻֮
        cp ${bakdir}/${_version}/${rollFile} ${rollFile}
    done
    print_format "�ѻع���${_version}�汾"
}

hsdeployApp() {
    # ICS��Ŀ����
    print_format "��ʼICS����..."
    local _error_ _status_
    _error_=`/usr/bin/unzip -od ${appdir} ${tmpdir}/${filename} 2>&1 1>/dev/null`
    _status_=$?

    if [ ${_status_} != 0 ];then
        print_format "����ʧ��,��ϸ��Ϣ����:"
        print_format "${_error_}"
        exit 2
    else
        print_format "���벿�����"
    fi
}




#### ��� ####

# ��һ��У��
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
        print_format "${_main}��δ֪ģʽ"
        exit 3
        ;;
esac

