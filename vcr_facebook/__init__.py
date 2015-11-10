from __future__ import absolute_import, unicode_literals, print_function

from .request import wrap_before_record
from .response import wrap_before_record_response
from .util import identity


def get_vcr_kwargs(vcr_kwargs=None, **kwargs):
    if vcr_kwargs is None:
        vcr_kwargs = {}
    return dict(
        vcr_kwargs,
        before_record=wrap_before_record(
            vcr_kwargs.get('before_record', identity), **kwargs),
        before_record_response=wrap_before_record_response(
            vcr_kwargs.get('before_record_response', identity), **kwargs),
    )


__all__ = ['get_vcr_kwargs']
