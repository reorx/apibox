#!/usr/bin/env python
# coding: utf-8


def to_utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf8')
    return s
