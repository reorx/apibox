#!/usr/bin/env python
# coding: utf-8

"""
``foo_api_def.yml``:

base_url: 'http://127.0.0.1:8000'
requests:
    - uri: /api/foo
      method: POST
      requests:
          - data:
              key-a: v-a
              key-b: v-b
          - data:
              key-A: v-A
              key-B: v-B
    - uri: /api/bar
      method: GET
      requests:
          - params:
              query-a: v-a
              query-b: v-b


``foo_api_test.py``:

from apibox.testing import yield_requests


def test_foo_api():
    for request_func, args in yield_requests(__file__, 'foo_api_test.yml'):
        yield request_func, args


Run using nosetest:
$ nosetests -s foo_api_test.py
"""

import requests
import requests.models
import json
import yaml
import copy
import types
import os


class RequestArguments(object):
    def __init__(self, arguments):
        if 'url' not in arguments:
            if 'base_url' in arguments:
                url = arguments['base_url'] + arguments['uri']
            else:
                url = arguments['uri']
            arguments['url'] = url
        self.arguments = arguments

    @property
    def data_str(self):
        data = self.arguments.get('data')
        if data:
            return json.dumps(data, ensure_ascii=False).encode('utf8')
        return ''

    @property
    def params_str(self):
        params = self.arguments.get('params')
        if params:
            return requests.models.RequestEncodingMixin._encode_params(params)
        return ''

    def __str__(self):
        d = dict(self.arguments)
        if 'data' in self.arguments:
            short = self.data_str[:50]
        elif 'params' in self.arguments:
            short = self.params_str[:50]
        else:
            short = ''
        d['params_or_data_short'] = short
        return '{method} {url} {params_or_data_short}'.format(**d)

    def __repr__(self):
        return str(self)


def do_request(req_args):
    args = req_args.arguments
    func = getattr(requests, args['method'].lower())
    kwargs = {i: args[i] for i in args
              if i in ['params', 'data', 'headers', 'cookies']}
    resp = func(args['url'], **kwargs)
    print resp.status_code, resp.content
    assert resp.status_code == 200


def yield_args(args, df):
    _args = copy.copy(df)
    if 'requests' in _args:
        reqs = _args.pop('requests')
        args.update(_args)
        for child_df in reqs:
            yielded = yield_args(copy.copy(args), child_df)
            if isinstance(yielded, types.GeneratorType):
                for i in yielded:
                    yield i
            else:
                yield yielded
    else:
        args.update(_args)
        yield args


def yield_requests(current_path, filename):
    filepath = os.path.join(
        os.path.dirname(current_path), filename)
    with open(filepath, 'r') as f:
        requests_def = yaml.load(f.read())

    for args in yield_args({}, requests_def):
        yield do_request, RequestArguments(args)
