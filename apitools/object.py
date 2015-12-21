#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import urlencode
import requests
from .log import logger


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
    default_content_type = 'text'  # or 'json'
    token_config = None
    #token_config = {
    #    'in': 'params',  # or 'headers'
    #    'key': None
    #}

    def __init__(self, token=None):
        # Check attributes
        if not self.base_url:
            raise ValueError('`base_url` is required')
        if not self.uris:
            raise ValueError('`uris` is required')

        if self.token_config:
            if not self.token_config.get('key'):
                raise ValueError('`key` in `token_config` is required')

            # Set token
            if token:
                self.token_config['value'] = token

            if not self.token_config.get('value'):
                raise ValueError('if `token_config` is set, `token` must be set or passed')
        else:
            if token:
                raise ValueError('`token_config` must be set to pass `token` into it')

    def __getattr__(self, name):
        return ResourcePath(self, name)

    def get_url(self, uri, params=None):
        url = self.base_url + uri
        if params:
            url += '?' + urlencode(params)
        return url

    def get_headers(self):
        headers = {}
        if self.token_is_in('headers'):
            token_key = self.token_config['key']
            headers[token_key] = self.token_config['value']
        return headers

    def token_is_in(self, position):
        if not self.token_config:
            return False
        return position == self.token_config['in']

    def make_req(self, uri, *args, **kwargs):
        """
        kwargs:
        - params

        uri supported options:
        {
            'method': 'GET',
            'content_type': 'text',
            'default_params': {'a': 1},
        }
        """
        try:
            options = self.uris[uri]
        except KeyError:
            raise Exception('URI %s is not in uris' % uri)
        method = options['method'].lower()

        # handle `content_type`
        content_type = options.get('content_type', self.default_content_type)

        # handle `default_params`
        params = options.get('default_params', {})
        passing_params = kwargs.get('params', {})
        params.update(passing_params)

        # handle token
        if self.token_is_in('params'):
            token_key = self.token_config['key']
            params[token_key] = self.token_config['value']

        url = self.get_url(uri, params)
        headers = self.get_headers()
        requester = getattr(requests, method)

        logger.info('[REQUEST] %s %s', requester.__name__, uri)
        resp = requester(url, headers=headers)

        if content_type == 'json':
            return resp.json()
        else:  # == 'text'
            return resp.content


class ResourcePath(object):
    def __init__(self, api, name, parent=None):
        self._api = api
        self._name = name
        self._parent = parent

    def __getattr__(self, name):
        return ResourcePath(self._api, name, self)

    def __call__(self, *args, **kwargs):
        return self._api.make_req(self.get_path(), *args, **kwargs)

    def get_path(self):
        names = []

        rp = self
        while rp is not None:
            names.insert(0, rp._name)
            rp = rp._parent

        return '/' + '/'.join(names)

    def __str__(self):
        return '<ResourcePath %s>' % self.get_path()
