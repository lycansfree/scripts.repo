#!/usr/bin/env python
# coding:utf-8

# 正则解析tnsnames.ora
import re

recp = re.compile("^(\w+?)\s?=.*?HOST\s?=\s?(.+?)\).*?PORT\s?=\s?(\d+?)\).*?SERVICE_NAME\s?=\s?(.+?)\)",re.M + re.S)
