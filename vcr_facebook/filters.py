from __future__ import absolute_import, unicode_literals, print_function

from collections import MutableMapping
from functools import wraps
import hashlib
import json
import logging
import re
import zlib

from .compat import OrderedDict, parse_qsl, quote
from . import multipart


logger = logging.getLogger(__name__)


class BaseParser(MutableMapping):

    def __init__(self, raw, ignore_exceptions=True):
        self.raw = raw
        self.ignore_exceptions = ignore_exceptions
        try:
            self.parsed = self._parse(raw)
        except Exception:
            if ignore_exceptions:
                self.parsed = None
            else:
                raise

    def __str__(self):
        return (self._unparse(self.parsed, self.raw)
                if self.parsed is not None else
                self.raw)

    def _parse(self, raw):
        raise NotImplementedError

    def _unparse(self, parsed, raw):
        raise NotImplementedError

    def __getitem__(self, key):
        if self.parsed is None:
            raise KeyError
        return self.parsed[key]

    def __setitem__(self, key, value):
        self.parsed[key] = value

    def __delitem__(self, key):
        del self.parsed[key]

    def __iter__(self):
        return iter(self.parsed or [])

    def __len__(self):
        return len(self.parsed or [])

    def __nonzero__(self):
        return bool(self.parsed)

    def __getattr__(self, key):
        return getattr(self.parsed, key)

    def __setattr__(self, key, value):
        if key not in vars(self):
            parsed = vars(self).get('parsed')
            if hasattr(parsed, key):
                setattr(parsed, key, value)
                return
        vars(self)[key] = value


class QueryParser(BaseParser):

    def _parse(self, raw):
        return OrderedDict(
            parse_qsl(raw, keep_blank_values=True, strict_parsing=True)
        )

    def _unparse(self, parsed, raw):
        return '&'.join('{}={}'.format(quote(k), quote(v))
                        for k, v in parsed.items())


class UrlParser(QueryParser):

    def _parse(self, raw):
        self.__base, _, q = raw.partition('?')
        return super(UrlParser, self)._parse(q)

    def _unparse(self, parsed, raw):
        q = super(UrlParser, self)._unparse(parsed, raw)
        return '{}{}{}'.format(self.__base, '?' if q else '', q)


class MultipartParser(BaseParser):

    def _parse(self, raw):
        return multipart.MultiPartFormData(raw)

    def _unparse(self, parsed, raw):
        return str(parsed)


class BatchParser(BaseParser):

    def _parse(self, raw):
        return json.loads(raw)

    def _unparse(self, parsed, raw):
        return json.dumps(parsed, sort_keys=True, separators=(',', ':'))


def make_filter(filter, parser_class, **kwargs):
    @wraps(filter)
    def wrapper(raw):
        data = parser_class(raw, **kwargs)
        if data:
            data = filter(data)
            raw = str(data)
        return raw
    return wrapper


def make_query_filter(filter, **kwargs):
    return make_filter(filter, QueryParser, **kwargs)


def make_url_filter(filter, **kwargs):
    return make_filter(filter, UrlParser, **kwargs)


def make_multipart_filter(filter, **kwargs):
    return make_filter(filter, MultipartParser, **kwargs)


def make_elider_filter(key, fun, prefix):
    def filter(data):
        if key in data and (not prefix or
                            not data[key].startswith(prefix)):
            value = fun(data) if fun else None
            if not value:
                value = fallback_elider(data[key])
            data[key] = prefix + value
        return data
    return filter


def fallback_elider(orig):
    if not isinstance(orig, bytes):
        orig = orig.encode('utf-8')
    return hashlib.md5(orig).hexdigest()


def make_batch_relative_url_filter(filter, **kwargs):
    url_filter = make_url_filter(filter, **kwargs)
    def batch_relative_url_filter(raw):
        query = QueryParser(raw, **kwargs)
        if query and 'batch' in query:
            batch = BatchParser(query['batch'], **kwargs)
            if batch:
                for req in batch:
                    if 'relative_url' in req:
                        req['relative_url'] = url_filter(req['relative_url'])
                query['batch'] = str(batch)
            raw = str(query)
        return raw
    return batch_relative_url_filter
