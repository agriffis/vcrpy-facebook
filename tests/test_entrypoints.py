from __future__ import absolute_import, unicode_literals

import os
from mock import MagicMock as Mock

import vcr_facebook


def test_get_vcr_kwargs():

    kwargs = vcr_facebook.get_vcr_kwargs()
    assert sorted(kwargs.keys()) == [
        'before_record',
        'before_record_response',
    ]
    assert callable(kwargs['before_record'])
    assert callable(kwargs['before_record_response'])


def test_get_vcr_kwargs_more():

    before_record = Mock()
    before_record_response = Mock()

    kwargs = dict(
        before_record=before_record,
        before_record_response=before_record_response,
        filter_headers=['foo'],
        filter_query_parameters=['bar'],
        filter_post_data_parameters=['baz'],
    )

    elide_appsecret_proof = Mock()
    elide_access_token = Mock()
    elide_client_secret = Mock()

    kwargs = vcr_facebook.get_vcr_kwargs(
        kwargs,
        elide_appsecret_proof=elide_appsecret_proof,
        elide_access_token=elide_access_token,
        elide_client_secret=elide_client_secret,
    )

    assert sorted(kwargs.keys()) == [
        'before_record',
        'before_record_response',
        'filter_headers',
        'filter_post_data_parameters',
        'filter_query_parameters',
    ]
