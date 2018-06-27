# -*- coding: utf-8 -*-

import os
import yaml
from apibox.testing import yield_requests


dirname = os.path.dirname(__file__)


def test_yield_requests():
    filepath = os.path.join(dirname, 'data/foo_api_def.yml')
    arguments_list = []
    for func, reqargs in yield_requests(filepath, yaml.load):
        arguments_list.append(reqargs.arguments)

    # POST /api/foo
    arguments = arguments_list[0]
    print(arguments)
    assert arguments['url'] == 'http://127.0.0.1:8000/api/foo'
    assert arguments['method'] == 'POST'
    assert arguments['data'] == {'key-b': 'v-b', 'key-a': 'v-a'}

    # POST /api/foo
    arguments = arguments_list[1]
    print(arguments)
    assert arguments['url'] == 'http://127.0.0.1:8000/api/foo'
    assert arguments['method'] == 'POST'
    assert arguments['data'] == {'key-A': 'v-A', 'key-B': 'v-B'}

    # GET /api/bar
    arguments = arguments_list[2]
    print(arguments)
    assert arguments['url'] == 'http://127.0.0.1:8000/api/bar'
    assert arguments['method'] == 'GET'
    assert arguments['params'] == {'query-a': 'v-a', 'query-b': 'v-b'}
