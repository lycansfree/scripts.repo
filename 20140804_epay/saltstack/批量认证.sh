#!/bin/bash

for homedir in `cat /etc/passwd | awk -F ":" '{if($4 == 8888) print $6}'`
do
    user=`ls -ld ${homedir} | awk '{print $3}'`
    group=`ls -ld ${homedir} | awk '{print $4}'`
    sshdir="${homedir}/.ssh"
    filename="authorized_keys"
    if [ ! -d ${sshdir} ];then
        mkdir -p ${sshdir}
        chown -R ${user}:${group} ${sshdir}
        chmod 700 ${sshdir}
    fi

    grep 'wzf@bjgg-L-73-app10' ${sshdir}/${filename} 1>/dev/null 2>&1
    if [ $? != 0 ];then
        echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDGMiCsglouX52CdgiZn/ECyWj4CSwKG9f81np/pmBuoalb0YmgjqoZZn8VuB3gsRzNrOJ7a7d0CH8jq3pZU+ROyCPU6d/W2FLH+ebUjplwEyR7v3GHiLZTPFwefFCUNDagqrAXh62O6nnw3KeeKNazTvU76rdsGgEqNCYYkU9i1PLC7afA1X8Bmaou2A7BTc1TeM/jjq1Jdi4Mb8jeDEtim5QGW4Rnz3x2Prtgsf3tMh/N5YC1KcnJoV/wFK/Aaq7c3LYmQ2OFCfZnYo1ued0o45xFJoKCB7UzCjedK2WsT8VNB7Yb6qfHCo5lZRxa4YcrDZpTtpClM8vEB8PRRgtj wzf@bjgg-L-73-app10" >> ${sshdir}/${filename}

        chown ${user}:${group} ${sshdir}/${filename}
    fi
    chmod 600 ${sshdir}/${filename}
done
