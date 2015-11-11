from __future__ import absolute_import, unicode_literals, print_function

import hashlib
import logging
import re
import zlib

from .compat import OrderedDict, parse_qsl, quote
from .filters import (make_batch_relative_url_filter, make_multipart_filter, make_query_filter,
                      make_url_filter, make_elider_filter)
from .util import always_return


logger = logging.getLogger(__name__)


def wrap_before_record(wrapped, **kwargs):
    before_record = make_before_record(**kwargs)
    def wrapper(request):
        request = before_record(request)
        request = wrapped(request)
        return request
    return wrapper


def make_before_record(elide_appsecret_proof,
                       elide_access_token,
                       elide_client_secret,
                       elider_prefix):

    appsecret_proof_filter = make_elider_filter(
        'appsecret_proof',
        elide_appsecret_proof and (
            lambda q: elide_appsecret_proof(q['appsecret_proof'],
                                            q['access_token'])),
        elider_prefix,
    )

    access_token_filter = make_elider_filter(
        'access_token',
        elide_access_token and (
            lambda q: elide_access_token(q['access_token'])),
        elider_prefix,
    )

    client_secret_filter = make_elider_filter(
        'client_secret',
        elide_client_secret and (
            lambda q: elide_client_secret(q['client_secret'])),
        elider_prefix,
    )

    def _filter_body(body):
        filters = [
            make_multipart_filter(filter_uploads),
            make_batch_relative_url_filter(appsecret_proof_filter),
            make_batch_relative_url_filter(access_token_filter),
            make_batch_relative_url_filter(client_secret_filter),
            make_query_filter(appsecret_proof_filter),
            make_query_filter(access_token_filter),
            make_query_filter(client_secret_filter),
            make_multipart_filter(appsecret_proof_filter),
            make_multipart_filter(access_token_filter),
            make_multipart_filter(client_secret_filter),
        ]
        for f in filters:
            body = f(body)
        return body

    def _filter_headers(headers):
        if 'content-length' in headers:
            del headers['content-length']
        return headers

    def _filter_url(url):
        filters = [
            make_url_filter(appsecret_proof_filter),
            make_url_filter(access_token_filter),
            make_url_filter(client_secret_filter),
        ]
        for f in filters:
            url = f(url)
        return url

    def before_record(request):
        if request.host != 'graph.facebook.com':
            return request
        request.body = _filter_body(request.body)
        request.headers = _filter_headers(request.headers)
        request.url = _filter_url(request.url)
        request = filter_multipart_boundary(request)
        return request
    return before_record


def filter_uploads(parts):
    for p in parts:
        if b'; filename="' in p.header and len(p.content) > 100:
            p.content = hashlib.md5(p.content).hexdigest()
    return parts


MULTIPART_BOUNDARY = b'xxBOUNDARY' * 10

def filter_multipart_boundary(request):
    content_type = request.headers.get('content-type', '')
    prefix, equals, boundary = content_type.partition('=')
    if boundary and prefix == 'multipart/form-data; boundary':
        boundary = MULTIPART_BOUNDARY[:len(boundary)]
        request.headers['content-type'] = b'{0}={1}'.format(prefix, boundary)
        def filter(parts):
            assert len(parts.boundary) == len(boundary)
            parts.boundary = boundary
            return parts
        request.body = make_multipart_filter(filter)(request.body)
    return request
