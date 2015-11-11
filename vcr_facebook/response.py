from __future__ import absolute_import, unicode_literals, print_function

import collections
import copy
import json
import logging
import re
import zlib

from .compat import OrderedDict, parse_qsl, quote
from .filters import fallback_elider


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

        # The response at this point is both (1) what will be recorded, and
        # (2) what will be returned to the application. The problem is that a
        # test needs to run through with the original responses the first time,
        # so that paging links with embedded access tokens are still valid.
        # Later when the test replays in full, the elided tokens will match
        # from the response and the request for the next page, but the first
        # time we have to be careful not to break the paging links.
        response = copy.deepcopy(response)

        response = ungzip(response)
        response = filter_access_tokens(
            response, elide_access_token, elider_prefix)
        response = update_content_length(response)
        return response
    return before_record_response


def ungzip(response):
    headers, body = response['headers'], response['body']

    if 'gzip' in headers.get('content-encoding', []):
        body['string'] = zlib.decompress(body['string'], 16 + zlib.MAX_WBITS)
        headers['content-encoding'].remove('gzip')
        if not headers['content-encoding']:
            del headers['content-encoding']

    return response


def filter_access_tokens(response,
                         elide_access_token,
                         elider_prefix):

    # One approach would be to detect batch responses, then branch
    # accordingly. Either know in advance all the places that access tokens
    # can appear, or use something like jsonpath-rw to find them. But in
    # fact access tokens only appear in two forms in the JSON response:
    #
    #   "access_token":"..."  in JSON
    #   access_token=...      in paging URLs
    #
    # so it's much easier to use regular expression matching.

    # Decode so unicode patterns can operate on the body.
    body = response['body']['string'].decode('utf-8')

    body = re.sub(
        r'"access_token":\s*"([^"]+)"',
        lambda m: '"access_token":"{0}"'.format(
            elide(m.group(1), elide_access_token, elider_prefix)),
        body,
    )

    body = re.sub(
        r'access_token=([^&"]+)',
        lambda m: 'access_token={0}'.format(
            elide(m.group(1), elide_access_token, elider_prefix)),
        body,
    )

    response['body']['string'] = body.encode('utf-8')
    return response


def elide(orig, fun, prefix):
    if prefix and orig.startswith(prefix):
        return orig
    value = None
    if fun:
        value = fun(orig)
    if not value:
        value = fallback_elider(orig)
    return prefix + value


def update_content_length(response):
    headers, body = response['headers'], response['body']
    if 'content-length' in headers:
        headers['content-length'] = [str(len(body['string']))]
    return response
