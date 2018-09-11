#!/bin/bash

# the shell script will install salt-minion

# determine current user
username=`whoami`
if [ "${username}" != "suweihu" ];then
    echo "Need suweihu user"
    exit 2
fi

# determine os release
#release=`cat /etc/redhat-release | grep -oE "[0-9]+\.?[0-9]+" | awk '{print substr($0,0,1)}'`
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

# whether has been installed
rpm -qa | grep salt-minion 1>/dev/null
if [ $? == 0 ];then
    echo "Already install salt-minion"
    sudo grep -vE "^$|^#" /etc/salt/minion
    exit 0
fi

# function to edit the minion conf
initConf() {
    _localIP=`ifconfig | grep -oE "192\.168\.[0-9]+\.[0-9]+" | grep -vE "255$" | head -1`
    sudo su - root -c "echo -e '\nmaster: 192.168.11.211\nid: ${_localIP}\n' >> /etc/salt/minion"
}

# first,update inner repo
basedir=$(cd `dirname $0`;pwd)
mkdir -p ${basedir}/repobak
sudo mv /etc/yum.repos.d/* ${basedir}/repobak
sudo su - root -c 'echo -e "[salt-local]\nname=saltstack\nbaseurl=http://192.168.80.109/salt-latest\nenabled=1\ngpgcheck=0" > /etc/yum.repos.d/salt.repo'
# clean all cache
sudo yum clean all

# second,test yum instal salt-minion
sudo yum -y install python-libs python-devel salt-minion
if [ $? == 0 ];then
    # succ & update the /etc/salt/minion
    initConf
else
    # fail & update the python-libs
    sudo yum -y install python-libs python-devel
    if [ $? == 0 ];then
        sudo yum -y install salt-minion
    else
        echo "yum install failed"
        exit 2
    fi
    initConf
fi

sudo service salt-minion start
sudo grep -vE "^$|^#" /etc/salt/minion

