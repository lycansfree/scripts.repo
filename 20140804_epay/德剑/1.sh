#!/bin/bash

# 调整inputFile即可，如果要输出到outputFile，可以使用外部重定向的方式
inputFile="a"
#outputFile=""

cat ${inputFile} | awk '{if($1 ~ "[0-9]+") print $0}' | while read line
do
    name=`echo ${line} | awk '{print $3}'`
    wwn=`echo ${line} | awk '{print $4}'`
    _name=`echo ${name} | awk -F "_" '{printf "huawei/%s-%s%s",$2,$4,substr($5,4)}'`
    printf "KERNEL==\"sd*\", BUS==\"scsi\", PROGRAM==\"/sbin/scsi_id -g -u /dev/\\\$name\", RESULT==\"3%s\", NAME=\"%s\", OWNER=\"grid\", GROUP=\"oinstall\", MODE=\"0660\"\n" ${wwn} ${_name}
done
