#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


class APIBase(object):
    """
    Usage:

    >>> class PinboardAPI(APIBase):
    ...     base_url = 'https://api.pinboard.in/v1'
    ...     uris = {
    ...         '/posts/all': {
    ...             'method': 'GET'
    ...         },
    ...         '/posts/recent': {
    ...             'method': 'GET'
    ...         },
    ...     }
    >>> api = API(token)
    >>> body = api.posts.all(raw=True)
    """
    base_url = None
    uris = None
    token = None

    def __init__(self, token):
        self.token = token

    def __getattr__(self, name):
        return ResourcePath(self, name)

    def get_url(self, uri):
        return self.base_url + uri + '?auth_token=%s' % self.token

    def make_req(self, uri):
        try:
            options = self.uris[uri]
        except KeyError:
            raise Exception('URI %s is not in uris' % uri)
        method = options['method'].lower()

        requester = getattr(requests, method)
        url = self.get_url(uri)
        print '[REQUEST] %s %s' % (requester.__name__, uri)
        resp = requester(url)
        return resp.content


class ResourcePath(object):
    def __init__(self, api, name, parent=None):
        self._api = api
        self._name = name
        self._parent = parent

    def __getattr__(self, name):
        return ResourcePath(self._api, name, self)

    def __call__(self, *args, **kwargs):
        return self._api.make_req(self.get_path())

    def get_path(self):
        names = []

        rp = self
        while rp is not None:
            names.insert(0, rp._name)
            rp = rp._parent

        return '/' + '/'.join(names)

    def __str__(self):
        return '<ResourcePath %s>' % self.get_path()
