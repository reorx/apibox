#!/usr/bin/env python
# coding: utf-8

import sys


PY2 = sys.version_info.major == 2


def to_utf8(s):
    if PY2:
        if isinstance(s, unicode):
            return s.encode('utf8')
    return s
