#!/usr/bin/env python
# coding:utf-8

import re
import pexpect
import time

def ceshi():
    commands = 'fdisk /dev/xvda'
    pep = ['：',': ',pexpect.EOF,pexpect.TIMEOUT]
    try:
        fdisk = pexpect.spawn(commands)
        time.sleep(0.3)

        index = fdisk.expect(pep)

        if index == 0:
            fdisk.sendline('p')
        else:
            raise IOError('close')



