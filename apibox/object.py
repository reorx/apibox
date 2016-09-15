#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import requests
from urllib import urlencode
from .log import logger
from .utils import to_utf8

# TODO support:
# api.notes.GET()
# api.notes['123'].GET()


# TODO uri alias

CONTENT_TYPE_HEADER_MAP = {
    'text': 'text/plain; charset=utf-8',
    'json': 'application/json; charset=utf-8',
    'form': 'application/x-www-form-urlencoded; charset=utf-8',
    'multipart': 'multipart/form-data; charset=utf-8; boundary=__X_APIBOX_BOUNDARY__',
}


class APIBaseMeta(type):
    def __new__(cls, name, bases, attrs):
        uris = attrs.get('uris')
        method_defs = {}
        if uris:
            for uri, options in uris.iteritems():
                method_parts = []
                template_parts = []
                args = []
                for seg in filter(lambda x: x, uri.split('/')):
                    if re.search(r'^\(.+\)$', seg):
                        template_parts.append('{}')
                        args.append(
                            re.compile(seg)
                        )
                    else:
                        method_parts.append(seg)
                        template_parts.append(seg)

                method_defs['.'.join(method_parts)] = {
                    'uri_template': '/' + '/'.join(template_parts),
                    'args': args,
                    'options': options
                }

        attrs['method_defs'] = method_defs

        return type.__new__(cls, name, bases, attrs)


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
    __metaclass__ = APIBaseMeta

    base_url = None
    uris = None
    default_content_type = 'text'  # or 'json', 'form'
    token_config = None
    #token_config = {
    #    'in': 'params',  # or 'headers'
    #    'key': None,
    #    'value': None,
    #}
    timeout = None

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

    def get_url(self, uri):
        url = self.base_url + uri
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
        if content_type in CONTENT_TYPE_HEADER_MAP:
            _headers['Content-Type'] = CONTENT_TYPE_HEADER_MAP[content_type]
        else:
            _headers['Content-Type'] = content_type

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

    def call_method(self, method_path, *args, **kwargs):
        # print 'call_method', method_path, args, kwargs
        if method_path not in self.method_defs:
            raise ValueError('No uri for {} method'.format(method_path))

        method_def = self.method_defs[method_path]
        argps = method_def['args']
        if len(args) != len(argps):
            raise ValueError('Invalid arguments number, get {}, should be {}'.format(len(args), len(argps)))

        for i, argp in enumerate(argps):
            arg = args[i]
            rv = argp.match(str(arg))
            if not rv:
                raise ValueError('{}st Argument {} not match with {}'.format(i, arg, argp))

        uri = method_def['uri_template'].format(*args)

        return self._make_req(uri, method_def['options'], **kwargs)

    def _make_req(self, uri, options, params=None, data=None, headers=None, files=None, **kwargs):
        """
        kwargs:
        - params
        - date
        - headers
        - files

        uri supported options:
        {
            'method': 'GET',
            'content_type': 'text',
            'default_params': {'a': 1},
            'default_headers': {'b': 'B'},
        }
        :raises: RequestsError
        """
        method_lower = options['method'].lower()

        self.check_arguments(options, params, data, headers, files)

        # get params
        params = self.get_params(options, params)

        # get data
        data = self.get_data(options, data)

        # get headers
        headers = self.get_headers(options, headers)

        # get url
        url = self.get_url(uri)

        # set default kwargs
        if self.timeout is not None:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = self.timeout

        requester = getattr(requests, method_lower)

        # print 'uri', uri
        logger.info('[REQUEST] %s %s; Headers: %s', requester.__name__, url, headers)
        try:
            resp = requester(
                url, params=params,
                data=data,
                headers=headers,
                files=files,
                **kwargs)
        except Exception as e:
            raise RequestsError('requests failed by: {} - {}'.format(type(e), e))

        logger.info('[RESPONSE] %s %s', resp.status_code, resp.content[:200])
        return self.process_response(uri, options, resp)

    def process_response(self, uri, options, resp):
        """Override to implement how to process the response for each request"""
        return resp


class ResourcePath(object):
    def __init__(self, api, name, parent=None):
        self._api = api
        self._name = name
        self._parent = parent

    def __getattr__(self, name):
        return ResourcePath(self._api, name, self)

    def __call__(self, *args, **kwargs):
        method_path = self.get_path()
        return self._api.call_method(method_path, *args, **kwargs)

    def get_path(self):
        names = []

        rp = self
        while rp is not None:
            names.insert(0, rp._name)
            rp = rp._parent

        return '.'.join(names)

    def __str__(self):
        return '<ResourcePath %s>' % self.get_path()


class InvalidRequestArguments(Exception):
    pass


class RequestsError(Exception):
    """requests failed"""
