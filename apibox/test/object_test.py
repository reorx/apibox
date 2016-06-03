#!/usr/bin/env python
# coding: utf-8

import logging
from nose.tools import assert_raises
from nose.plugins.attrib import attr
from urllib import urlencode
from apibox.object import APIBase


logging.basicConfig(level=logging.INFO)


@attr('basic')
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

    print BinAPI.method_defs

    api = BinAPI()
    resp = api.get.wtf('hello')
    print 'resp', resp


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
    print type(body)

    print body['url']
    assert body['url'] == BinAPI.base_url + '/get'


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
    body = api.get(params={'c': 1})

    print body['url']
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

    token = 'asdf123'

    # No token, raise
    with assert_raises(ValueError):
        api = BinAPI()

    # token in url
    api = BinAPI(token)
    body = api.get()

    print 'url', body['url']
    assert body['url'] == BinAPI.base_url + '/get?' + urlencode({'a': 'b', 'token': token})

    # token in header
    BinAPI.token_config['in'] = 'headers'
    BinAPI.token_config['key'] = 'X-Token'
    api = BinAPI(token)
    body = api.get()

    print 'headers', body['headers']
    assert body['headers'].get('X-Token') == token
