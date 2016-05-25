#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from urllib import urlencode
from .log import logger
from .utils import to_utf8

# TODO uri alias

CONTENT_TYPE_HEADER_MAP = {
    'text': 'text/plain; charset=utf-8',
    'json': 'application/json; charset=utf-8',
    'form': 'application/x-www-form-urlencoded; charset=utf-8',
    'multipart': 'multipart/form-data; charset=utf-8; boundary=__X_APIBOX_BOUNDARY__',
}


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
    default_content_type = 'text'  # or 'json', 'form'
    token_config = None
    #token_config = {
    #    'in': 'params',  # or 'headers'
    #    'key': None,
    #    'value': None,
    #}

    def __init__(self, token=None):
        # Check attributes
        if not self.base_url:
            raise ValueError('`base_url` is required')
        if not self.uris:
            raise ValueError('`uris` is required')

        if self.token_config:
            # To avoid instances writing a same dict object
            self.token_config = dict(self.token_config)

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

    def get_params(self, options, params):
        _params = options.get('default_params', {})
        _params.update(params or {})

        if self.token_is_in('params'):
            token_key = self.token_config['key']
            _params[token_key] = self.token_config['value']

        # ensure every k & v are str
        params = {to_utf8(k): to_utf8(v) for k, v in _params.iteritems()}
        return params or None

    def get_data(self, options, data):
        content_type = options.get('content_type', self.default_content_type)
        if data:
            if content_type == 'json':
                if isinstance(data, dict):
                    data = json.dumps(data)
                elif isinstance(data, str):
                    pass
                else:
                    raise InvalidRequestArguments(
                        '`data` should not be of type {} when content_type is json'.format(type(data)))
            return data
        else:
            return None

    def get_headers(self, options, headers):
        _headers = options.get('default_headers', {})
        _headers.update(headers or {})

        content_type = options.get('content_type', self.default_content_type)
        _headers['Content-Type'] = CONTENT_TYPE_HEADER_MAP[content_type]

        if self.token_is_in('headers'):
            token_key = self.token_config['key']
            _headers[token_key] = self.token_config['value']

        headers = _headers
        return headers or None

    def token_is_in(self, position):
        if not self.token_config:
            return False
        return position == self.token_config['in']

    def check_arguments(self, options, params, data, headers, files):
        method = options['method']
        # data is only allowed when POST, PUT, PATCH
        if data:
            if method not in ['POST', 'PUT', 'PATCH']:
                raise InvalidRequestArguments('`data` is not allowed on {}'.format(method))
        # files is only allowed when POST, PUT, PATCH
        if files:
            if method not in ['POST', 'PUT', 'PATCH']:
                raise InvalidRequestArguments('`files` is not allowed on {}'.format(method))

    def make_req(self, uri, params=None, data=None, headers=None, files=None, **kwargs):
        """
        kwargs:
        - params

        uri supported options:
        {
            'method': 'GET',
            'content_type': 'text',
            'default_params': {'a': 1},
            'default_headers': {'b': 'B'},
        }
        """
        try:
            options = self.uris[uri]
        except KeyError:
            raise Exception('URI %s is not in uris' % uri)
        method_lower = options['method'].lower()

        self.check_arguments(options, params, data, headers, files)

        # get params
        params = self.get_params(options, params)

        # get data
        data = self.get_data(options, data)

        # get headers
        headers = self.get_headers(options, headers)

        # get url
        url = self.get_url(uri, params)

        requester = getattr(requests, method_lower)

        logger.info('[REQUEST] %s %s; Headers: %s', requester.__name__, uri, headers)
        resp = requester(
            url, params=params, data=data, headers=headers,
            files=files, **kwargs)

        logger.info('[RESPONSE] %s %s', resp.status_code, resp.content[:100])
        return resp


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


class InvalidRequestArguments(Exception):
    pass
