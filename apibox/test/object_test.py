# -*- coding: utf-8 -*-

import logging
import pytest
from six.moves.urllib.parse import urlencode
from apibox.object import APIBase, RequestsError


logging.basicConfig(level=logging.INFO)


def test_define():
    class BinAPI(APIBase):
        base_url = 'http://httpbin.org'
        default_content_type = 'json'
        uris = {
            '/get': {
                'method': 'GET'
            },
            '/get/(\w+)/wtf': {
                'method': 'GET'
            },
        }

    print(BinAPI.method_defs)

    api = BinAPI()
    resp = api.get.wtf('hello')
    print('resp', resp)


def test_get():
    class BinAPI(APIBase):
        base_url = 'http://httpbin.org'
        default_content_type = 'json'
        uris = {
            '/get': {
                'method': 'GET'
            },
        }

    api = BinAPI()
    body = api.get()
    print(type(body))

    print(body)
    assert body.json()['url'] == BinAPI.base_url + '/get'


def test_get_with_params():
    class BinAPI(APIBase):
        base_url = 'http://httpbin.org'
        default_content_type = 'json'
        uris = {
            '/get': {
                'method': 'GET',
                'default_params': {
                    'a': 'b'
                }
            },
        }

    api = BinAPI()
    resp = api.get(params={'c': 1})
    print(resp)
    body = resp.json()

    print(body['url'])
    assert body['url'] == BinAPI.base_url + '/get?' + urlencode({'a': 'b', 'c': 1})


def test_get_with_token():
    class BinAPI(APIBase):
        base_url = 'http://httpbin.org'
        default_content_type = 'json'
        uris = {
            '/get': {
                'method': 'GET',
                'default_params': {
                    'a': 'b'
                }
            },
        }
        token_config = {
            'in': 'params',
            'key': 'token'
        }

    token = 'fake-token'

    # No token, raise
    with pytest.raises(ValueError):
        BinAPI()

    # token in url
    api = BinAPI(token)
    resp = api.get()
    print(resp)
    body = resp.json()

    print('url', body['url'])
    assert body['url'] == BinAPI.base_url + '/get?' + urlencode({'a': 'b', 'token': token})

    # token in header
    BinAPI.token_config['in'] = 'headers'
    BinAPI.token_config['key'] = 'X-Token'
    api = BinAPI(token)
    resp = api.get()
    print(resp)
    body = resp.json()

    print('headers', body['headers'])
    assert body['headers'].get('X-Token') == token


def test_timeout():
    class BinAPI(APIBase):
        base_url = 'http://httpbin.org'
        uris = {
            '/delay/(\d)': {
                'method': 'GET',
            },
        }
        timeout = 2

    api = BinAPI()
    with pytest.raises(RequestsError):
        resp = api.delay(3)
        print(resp)
