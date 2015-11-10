from __future__ import absolute_import, unicode_literals, print_function

from .request import wrap_before_record
from .response import wrap_before_record_response
from .util import identity


def get_vcr_kwargs(vcr_kwargs=None,
                   elide_appsecret_proof=None,
                   elide_access_token=None,
                   elide_client_secret=None):

    if vcr_kwargs is None:
        vcr_kwargs = {}

    make_before_record_kwargs = dict(
        elide_appsecret_proof=elide_appsecret_proof,
        elide_access_token=elide_access_token,
        elide_client_secret=elide_client_secret,
    )

    make_before_record_response_kwargs = dict(
        elide_access_token=elide_access_token,
    )

    return dict(
        vcr_kwargs,
        before_record=wrap_before_record(
            vcr_kwargs.get('before_record', identity),
            **make_before_record_kwargs),
        before_record_response=wrap_before_record_response(
            vcr_kwargs.get('before_record_response', identity),
            **make_before_record_response_kwargs),
    )


__all__ = ['get_vcr_kwargs']
