#!/bin/bash

# 以README.md文件中路径为准
workdir=$(cd `dirname $0`;pwd)
cd ${workdir}
basedir="${workdir%/*}"
config="${workdir}/README.md"

for x in `cat ${config} | grep -oP "(?<=^- )\w+"`
do
    currworkdir="${workdir}/${x}"
    currbasedir="${basedir}/${x}"
    # 创建目录
    test -d ${currworkdir} || mkdir -p ${currworkdir}
    cd ${currbasedir} || continue
    # 查找目录并创建对应
    # for y in `find . -type d | sed 1d`
    # do
    #     _tmp=${y#./}
    #     mkdir -p "${currworkdir}/${_tmp}"
    # done
    # 查找文件并复制对应
    for y in `find . -type f \
        -name "*.sh" -o \
        -name "*.py" -o \
        -name "*.yml" -o \
        -name "*.json"`
    do
        _tmp=${y#./}
        _tmpF=${_tmp##*/}
        if [ "${_tmp}" != "${_tmpF}" ];then
            mkdir -p "${currworkdir}/${_tmp%/*}"
        fi
        cp "${currbasedir}/${_tmp}" "${currworkdir}/${_tmp}"
    done
done
