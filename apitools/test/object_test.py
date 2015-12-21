#!/usr/bin/env python
# coding: utf-8

from nose.tools import assert_raises
from urllib import urlencode
from apitools.object import APIBase


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


def test_get_with_params_and_token():
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
            'in': ['params'],  # or contains 'header'
            'key': 'token'
        }

    with assert_raises(ValueError):
        api = BinAPI()

    token = 'asdf123'
    api = BinAPI(token)
    body = api.get()

    print body['url']
    assert body['url'] == BinAPI.base_url + '/get?' + urlencode({'a': 'b', 'token': token})
