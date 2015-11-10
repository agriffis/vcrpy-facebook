"""
Minimal hack for modifying multipart/form-data in HTTP traces.

This doesn't use cgi.parse_multipart() because that doesn't maintain key order.
It's easier to minimally disturb the data with split/join than a full parse.
"""
from __future__ import absolute_import, unicode_literals


CRNL = b'\r\n'
CRNL2 = CRNL * 2


class MultiPartFormData(object):
    """
    Get/set values in a multipart/form-data body.

    This doesn't bother with headers that precede the body, which means:

        1. It doesn't know about encodings. The body should be a byte string,
           and all methods operate on bytes rather than unicode. This is
           important because file upload data is typically raw bytes.

        2. The boundary is sniffed from the start of the body rather than being
           set by the header.

    How to use it:

        >>> parts = MultiPartFormData('---xxxboundary123\r\n'
                                      'Content-Disposition: form-data; name="access_token"\r\n'
                                      '\r\n'
                                      'abcde12345abcde12345\r\n')
        >>> parts.get('access_token')
        abcde12345abcde12345
        >>> parts['access_token'] = 'redacted'
        >>> str(parts)
        ---xxxboundary123
        Content-Disposition: form-data; name="access_token"

        redacted
    """

    def __init__(self, body):
        if isinstance(body, unicode):
            body = bytes(body)

        if not body.startswith(b'--'):
            raise ValueError("Doesn't appear to be a multipart/form-data")

        self.boundary = body.split(CRNL, 1)[0][2:]

        assert body.startswith(self._leader)
        assert body.endswith(self._terminator)

        inner_body = body[len(self._leader):-len(self._terminator)]
        self.parts = [MultiPartPart(p) for p in inner_body.split(self._splitter)]

    def __str__(self):
        inner_body = self._splitter.join(str(p) for p in self.parts)
        return b''.join([self._leader, inner_body, self._terminator])

    @property
    def parts(self):
        return self._parts

    @parts.setter
    def parts(self, parts):
        assert all(isinstance(p, MultiPartPart) for p in parts)
        self._parts = parts

    @property
    def _leader(self):
        return b'--' + self.boundary + CRNL

    @property
    def _splitter(self):
        return CRNL + b'--' + self.boundary + CRNL

    @property
    def _terminator(self):
        return CRNL + b'--' + self.boundary + b'--' + CRNL

    def find(self, key):
        name = b'; name="{}"'.format(key)
        for i, p in enumerate(self.parts):
            if name in p.header:
                return i
        return -1

    def __getitem__(self, key):
        i = self.find(key)
        if i < 0:
            raise KeyError
        return self.parts[i]

    def __contains__(self, key):
        return self.find(key) >= 0

    def __iter__(self):
        return iter(self.parts)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


class MultiPartPart(object):

    def __init__(self, s):
        assert isinstance(s, bytes)
        self.bytes = s

    def __str__(self):
        return self.bytes

    @property
    def header(self):
        return self.bytes.split(CRNL2, 1)[0]

    @header.setter
    def header(self, value):
        assert isinstance(value, bytes)
        self.bytes = CRNL2.join([value, self.content])

    @property
    def content(self):
        return self.bytes.split(CRNL2, 1)[1]

    @content.setter
    def content(self, value):
        self.bytes = CRNL2.join([self.header, value])
