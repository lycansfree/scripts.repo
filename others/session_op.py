#!/usr/bin/env python
# coding:utf-8

# session / cookie操作示例

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
import json
import urllib
import urllib2
import cookielib
import requests
from bs4 import BeautifulSoup
import os

EMPTYVARS = ('', [], None, {})

def make_cookie(name, value):
    return cookielib.Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain="six.it.bx",
        domain_specified=True,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=False,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
        rest=None
    )

def a():
    hosts = {
        'six': ['http://six.it.bx', 'accounts/login/?next=/secservice/', 'http://six.it.bx/fwauto/create_request/'],
        'aiops': ['http://aiops.it.bx', '_maintenance/login', 'http://aiops.it.bx/_maintenance/sysCode'],
        'itil': ['http://itil.it.bx', 'lemon/common/login.jsp', 'http://itil.it.bx/lemon/bpm/workspace-viewHistory.do?processInstanceId=1672564'],
        'wiki': ['http://wiki.it.bx', 'login.action?os_destination=%2Findex.action&permissionViolation=true', 'http://wiki.it.bx/display/bxyw/0813-0817']
    }
    host = hosts['wiki']
    initUrl = os.path.join(host[0], host[1])
    res = urllib2.urlopen(initUrl).read()
    soup = BeautifulSoup(res, "html.parser")
    try:
        uri = soup.form.get('action').strip('/')
        if uri == '#':
            url = initUrl
        else:
            url = os.path.join(host[0], uri)
    except Exception:
        url = initUrl

    data = {}
    for x in soup.form.find_all('input'):
        if x.get('type') == 'password':
            data[x.get('name')] = ''
        else:
            if x.get('value') in EMPTYVARS:
                data[x.get('name')] = 'zhoujie'
            else:
                data[x.get('name')] = x.get('value')

    print json.dumps(data, indent = 4)

    cookie = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(handler)

    req = urllib2.Request(url, urllib.urlencode(data))
    if 'csrfmiddlewaretoken' in data:
        # req.add_header('csrftoken', data['csrfmiddlewaretoken'])
        # data['csrftoken'] = data['csrfmiddlewaretoken']
        cookie.set_cookie(make_cookie('csrftoken', data['csrfmiddlewaretoken']))
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    res = opener.open(req)

    for item in cookie:
        print "%s=%s; path=/; domain=%s" % (item.name, item.value, item.domain)
        # print item.domain
        # print item.name
        # print item.value

    # res = opener.open(host[2])
    # print res.read()

def main():
    resp = requests.get('http://aiops.it.bx')
    cookie = resp.cookies.get_dict()
    url = 'http://aiops.it.bx/_maintenance/login'
    data = {
        'username': 'zhoujie',
        'password': ''
    }
    resp = requests.post(url, data = data, cookies = cookie)
    print resp.content


if __name__ == '__main__':
    a()

