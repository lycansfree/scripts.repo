#!/bin/bash
# 自动安装salt-minion
# 需要首先搭建内网源

. /etc/profile
if [ `whoami` != "root" ];then
    echo "Need ROOT role"
    exit 2
fi

release=`rpm -q python-libs | grep -oE "el[0-9]"`
platform=`uname -m`
if [ "${release}" != "el6" ];then
    echo "Need redhat-release 6"
    exit 2
fi

if [ "${platform}" != "x86_64" ];then
    echo "Need x86_64"
    exit 2
fi

# update inner repo
basedir=$(cd `dirname $0`;pwd)
mkdir -p ${basedir}/repobak
mv /etc/yum.repos.d/* ${basedir}/repobak
echo -e "[salt-local]\nname=saltstack\nbaseurl=http://192.168.80.109/salt-latest\nenabled=1\ngpgcheck=0" > /etc/yum.repos.d/saltLocal.repo
yum clean all

####################################################################################

# function to edit the minion conf
_localIP=`ifconfig | grep -oE "192\.168\.[0-9]+\.[0-9]+" | grep -vE "255$" | head -1`
if [ -z "${_localIP}" ];then
    echo "_localIP is null"
    exit 2
fi
_master="192.168.11.211"
_config="/etc/salt/minion"

initConf() {
    echo -e "\nmaster: ${_master}\nid: ${_localIP}\n" >> ${_config}
}

checkConf() {
    _id=`cat ${_config} | grep -E "^id" | grep -oE "192\.168\.[0-9]+\.[0-9]+"`
    conf_master=`cat ${_config} | grep -E "^master" | grep -oE "192\.168\.[0-9]+\.[0-9]+"`
    if [ "${_id}" == "${_localIP}" -a "${conf_master}" == "${_master}" ];then
        # ok
        return 0
    else
        # replace id
        sed -i "s/^id.*/id: ${_localIP}/" ${_config}
        sed -i "s/^master.*/master: ${_master}/" ${_config}
        return 1
    fi
}

# whether has been installed
rpm -q salt-minion 1>/dev/null 2>&1
if [ $? == 0 ];then
    # already install
    checkConf
    _flag=$?
else
    _flag=1
    # pre install
    yum -y install python-libs python-devel salt-minion
    if [ $? == 0 ];then
        # succ & update the /etc/salt/minion
        initConf
    else
        # fail & update the python-libs
        yum -y install python-libs python-devel
        if [ $? == 0 ];then
            yum -y install salt-minion
        else
            echo "yum install failed"
            exit 2
        fi
        initConf
    fi
fi

if [ ${_flag} == 1 ];then
    service salt-minion restart
fi

