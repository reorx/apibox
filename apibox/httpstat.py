#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curl
import pycurl
import sys


# https://github.com/pycurl/pycurl/blob/master/python/curl/__init__.py
# http://curl.haxx.se/libcurl/c/curl_easy_getinfo.html
# http://curl.haxx.se/libcurl/c/curl_easy_setopt.html
TIME_KEYS = [
    'namelookup',
    'connect',
    'appconnect',
    'pretransfer',
    'starttransfer',
    'total',
    'redirect'
]


OUTPUT = """Timeline:
|
|--NAMELOOKUP {namelookup}
|--|--CONNECT {connect}
|--|--|--APPCONNECT {appconnect}
|--|--|--|--PRETRANSFER {pretransfer}
|--|--|--|--|--STARTTRANSFER {starttransfer}
|--|--|--|--|--|--TOTAL {total}
|--|--|--|--|--|--REDIRECT {redirect}
"""

c = curl.Curl()

c.set_option(pycurl.FOLLOWLOCATION, 0)

c.get(sys.argv[1])

body = c.body()
print 'body', len(body), body[:20]
print 'header', c.header()

timeinfo = {}
for k, v in c.info().iteritems():
    if k.endswith('-time'):
        time_key = k[:-5]
        if time_key in TIME_KEYS:
            timeinfo[time_key] = v * 1000

for k in TIME_KEYS:
    if not k in timeinfo:
        timeinfo[k] = '?'

print OUTPUT.format(**timeinfo)

c.close()
