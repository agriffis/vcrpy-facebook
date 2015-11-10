from __future__ import absolute_import, unicode_literals, print_function

import logging
import re
import zlib

from .compat import OrderedDict, parse_qsl, quote
from .util import always_return


logger = logging.getLogger(__name__)


def wrap_before_record_response(wrapped, **kwargs):
    before_record_response = make_before_record_response(**kwargs)
    def wrapper(response):
        response = before_record_response(response)
        response = wrapped(response)
        return response
    return wrapper


def make_before_record_response(elide_access_token,
                                elider_prefix):

    def before_record_response(response):
        if 'facebook-api-version' not in response['headers']:
            return response

        response = ungzip(response)
        # replace top-level stuff
        # replace batch stuff
        return response
    return before_record_response


def ungzip(response):
    headers, body = response['headers'], response['body']

    if 'gzip' in headers.get('content-encoding', []):
        body['string'] = zlib.decompress(body['string'], 16 + zlib.MAX_WBITS)
        headers['content-encoding'].remove('gzip')
        if not headers['content-encoding']:
            del headers['content-encoding']
        response = update_content_length(response)

    return response


def update_content_length(response):
    headers, body = response['headers'], response['body']
    if 'content-length' in headers:
        headers['content-length'] = [str(len(body['string']))]
    return response
