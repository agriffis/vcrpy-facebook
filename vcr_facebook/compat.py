from __future__ import absolute_import, unicode_literals, print_function

try:
    from collections import OrderedDict
except ImportError:
    # python 2.6
    from ordereddict import OrderedDict

try:
    # python 3
    from urllib.parse import parse_qsl, quote
except ImportError:
    # python 2
    from urllib import quote
    from urlparse import parse_qsl
