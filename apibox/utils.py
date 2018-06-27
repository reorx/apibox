# -*- coding: utf-8 -*-

import six


def to_utf8(s):
    if six.PY2:
        if isinstance(s, six.text_type):
            return s.encode('utf8')
    return s
