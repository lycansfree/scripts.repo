#!/bin/bash --login

. ~/.bash_profile

workdir=$(cd `dirname $0`;pwd)
packages="zabbix-agent-3.2.1-1.el6.x86_64.rpm"

###########################function area start#######################################

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
    echo -e "${color_code}${content}\e[0m" >> ${workdir}/install_zabbix.log
}

package_exist() {
	for package in ${packages}
	do
		if [ ! -f "${workdir}/${package}" ];then
			print_color "��װ����ȱʧ" red
			exit 2
		fi
	done
}

rpm_install() {
	for package in ${packages}
	do
		rpm -ivh ${workdir}/${package}
		if [ $? != 0 ];then
			print_color "��װ��������" red
			exit 2
		fi
	done
}

edit_conf_alter() {
	local key=$1
	local value=$2
	sed -i "s:^${key}=.*:${key}=${value}:" /etc/zabbix/zabbix_agentd.conf
}

edit_conf_add() {
	local key=$1
	local value=$2
	sed -i "s:^\(\# ${key}.*\):\1\n\n${key}=${value}\n:" /etc/zabbix/zabbix_agentd.conf
	#another sed action
	#sed -i "/^# ${key}/a\ \n${key}=${value}\n" /etc/zabbix/zabbix_agentd.conf
}

###############################function end#############################################

# ����־��¼
cat /dev/null > ${workdir}/install_zabbix.log

if [ `whoami` != "root" ];then
	print_color "��Ҫroot�û�" red
	exit 2
fi

if [ `uname` != "Linux" ];then
	print_color "ֻ������Linux" red
	exit 2
fi

if [ `uname -i` != 'x86_64' ];then
	print_color "ֻ������64λϵͳ" red
	exit 2
fi

# ��鰲װ��
package_exist

# ��װ
rpm_install

if [ ! -f /etc/zabbix/zabbix_agentd.conf ];then
	print_color "zabbix_agentd.confȱʧ" red
	exit 2
fi

edit_conf_alter Server 192.168.80.110
edit_conf_alter ServerActive 192.168.80.110
edit_conf_alter Hostname `hostname`
edit_conf_add HostMetadataItem "system.uname"
edit_conf_add AllowRoot 1


service zabbix-agent restart

chkconfig --level 35 zabbix-agent on
