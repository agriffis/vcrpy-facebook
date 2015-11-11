from __future__ import absolute_import, unicode_literals, print_function

import copy
import json
import os
from mock import MagicMock as Mock

try:
    # python 3
    from urllib.parse import parse_qsl, quote, urlsplit
except ImportError:
    # python 2
    from urllib import quote
    from urlparse import parse_qsl, urlsplit

from vcr_facebook.request import make_before_record


def test_simple_request():
    request = MockRequest(
        url='https://graph.facebook.com/v2.4/me?access_token=AAAAAAAAAAAAAAAAAAAAAAAAAAAA',
    )
    new_request = MockRequest(
        url='https://graph.facebook.com/v2.4/me?access_token=XXX-35ea99843da5ff0639992be381c5b77a',
    )
    _test_request(request, new_request)
    return request, new_request  # for test_simple_request_idempotent


def test_simple_request_idempotent():
    request, new_request = test_simple_request()
    _test_request(request, new_request)


def test_batch_request():
    headers = get_request_headers()
    headers.update({
        'Content-Type': 'application/x-www-form-urlencoded',
    })
    batch_data = [
        {
            "method": "GET",
            "relative_url": "v2.4/111111111111111?access_token=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZ&appsecret_proof=YYYYYYYYYYYYYYYYYYYYYYYYYYYY&fields=name%2Ctimezone_id%2Cprimary_page%2Cvertical_id&summary=true"
        },
        {
            "body": "business_app=222222222222222",
            "method": "POST",
            "relative_url": "v2.4/333333333333333/applications?access_token=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZ&appsecret_proof=YYYYYYYYYYYYYYYYYYYYYYYYYYYY&summary=true"
        }
    ]
    batch = json.dumps(batch_data, sort_keys=True, separators=',:')
    body = '&'.join('{0}={1}'.format(quote(k), quote(v)) for k, v in [
        ('include_headers', 'true'),
        ('access_token', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAA'),
        ('batch', batch),
        ('appsecret_proof', 'BBBBBBBBBBBBBBBBBBBBBBBBBBBB'),
    ])
    request = MockRequest(
        method='POST',
        url='https://graph.facebook.com/',
        headers=headers,
        body=body,
    )
    new_body = body.replace('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZ', 'XXX-b610afc3e7ce9067b6fc49111cfadc14') \
                   .replace('YYYYYYYYYYYYYYYYYYYYYYYYYYYY', 'XXX-31ff6034e0c1aa2c665a0bd7de2dff65') \
                   .replace('AAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'XXX-35ea99843da5ff0639992be381c5b77a') \
                   .replace('BBBBBBBBBBBBBBBBBBBBBBBBBBBB', 'XXX-f41362dca518350fa6281cd27b14bf68')
    new_request = MockRequest(
        method='POST',
        url='https://graph.facebook.com/',
        headers=headers,
        body=new_body,
    )
    _test_request(request, new_request)
    return request, new_request  # for test_batch_request_idempotent


def test_batch_request_idempotent():
    request, new_request = test_batch_request()
    _test_request(request, new_request)


def _test_request(request, new_request, **kwargs):
    defaults = dict(
        elide_appsecret_proof=None,
        elide_access_token=None,
        elide_client_secret=None,
        elider_prefix='XXX-',
    )
    defaults.update(kwargs)
    before_record = make_before_record(**defaults)
    request = before_record(request)
    assert vars(request) == vars(new_request)


class MockRequest(object):
    def __init__(self, url, method='GET', headers=None, body=''):
        default_headers = get_request_headers()
        default_headers.update(headers or {})
        self.url = url
        self.method = method
        self.headers = default_headers
        self.body = body
    def __repr__(self):
        return '<MockRequest {0!r}>'.format(vars(self))
    def __eq__(self, other):
        return vars(self) == vars(other)
    def __getattr__(self, name):
        if name != 'url':
            return getattr(urlsplit(self.url), name)
        raise AttributeError
    @property
    def host(self):
        return self.hostname


def get_request_headers():
    return {
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'User-Agent': 'python-requests/2.7.0 CPython/2.7.6 Linux/4.2.3-300.fc23.x86_64',
    }
