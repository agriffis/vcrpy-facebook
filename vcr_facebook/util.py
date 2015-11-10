from __future__ import absolute_import, unicode_literals, print_function


def always_return(x):
    return lambda *args, **kwargs: x


def identity(x, *args, **kwargs):
    return x
