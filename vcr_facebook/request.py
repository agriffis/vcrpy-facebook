from __future__ import absolute_import, unicode_literals, print_function

from collections import OrderedDict
from functools import wraps
import hashlib
import logging
import re
import zlib

try:
    # python 3
    from urllib.parse import parse_qsl, quote
except ImportError:
    # python 2
    from urllib import quote
    from urlparse import parse_qsl

from .filters import (make_batch_relative_url_filter, make_multipart_filter, make_query_filter,
                      make_elider_with_fallback)
from .util import always_return


logger = logging.getLogger(__name__)


def wrap_before_record(wrapped, **kwargs):
    logger.debug("wrapping before_record")
    before_record = make_before_record(**kwargs)
    @wraps(wrapped)
    def wrapper(request):
        logger.debug("in before_record wrapper")
        request = before_record(request)
        request = wrapped(request)
        return request
    return wrapper


def make_before_record(elide_appsecret_proof=None,
                       elide_access_token=None,
                       elide_client_secret=None,
                       **kwargs):

    def _filter_body(body):
        appsecret_proof_filter = make_elider_with_fallback(
            'appsecret_proof', elide_appsecret_proof and (
                lambda q: elide_appsecret_proof(q['appsecret_proof'],
                                                q['access_token'])))
        access_token_filter = make_elider_with_fallback(
            'access_token', elide_access_token and (
                lambda q: elide_access_token(q['access_token'])))
        client_secret_filter = make_elider_with_fallback(
            'client_secret', elide_client_secret and (
                lambda q: elide_client_secret(q['client_secret'])))
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

    def before_record(request):
        if request.host != 'graph.facebook.com':
            return request

        # This check avoids running everything twice, since vcrpy calls for
        # can_play_response_for() as well as actually looking up the response.
        # This should really be fixed in vcrpy.
        if 'x-vcrpy' not in request.headers:
            request.body = _filter_body(request.body)
            request.headers = _filter_headers(request.headers)
            request = filter_multipart_boundary(request)
            request.headers['x-vcrpy'] = 'VCR.py was here'
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
        request.headers['content-type'] = b'{}={}'.format(prefix, boundary)
        def filter(parts):
            assert len(parts.boundary) == len(boundary)
            parts.boundary = boundary
            return parts
        request.body = make_multipart_filter(filter)(request.body)
    return request
