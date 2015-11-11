from __future__ import absolute_import, unicode_literals, print_function

import copy
import json
import os
from mock import MagicMock as Mock

from vcr_facebook.response import make_before_record_response


def test_simple_response():
    _test_response(get_response_headers(),
                   get_simple_response_data(),
                   new_simple_response_data())


def test_paged_response():
    _test_response(get_response_headers(),
                   get_paged_response_data(),
                   new_paged_response_data())


def test_batch_response():
    _test_response(get_response_headers(),
                   get_batch_response_data(),
                   new_batch_response_data())


def _test_response(headers, data, new_data, **kwargs):
    check_headers = copy.deepcopy(headers)
    response = mock_response(headers=headers, data=data)
    defaults = dict(
        elide_access_token=None,
        elider_prefix='XXX-',
    )
    defaults.update(kwargs)
    before_record_response = make_before_record_response(**defaults)
    response = before_record_response(response)

    content_length = int(response['headers']['content-length'][0])
    assert content_length == len(response['body']['string'])

    headers = dict((k, v) for k, v in response['headers'].items()
                   if k != 'content-length')
    check_headers = dict((k, v) for k, v in check_headers.items()
                         if k != 'content-length')
    assert headers == check_headers

    data = json.loads(response['body']['string'].decode('utf-8'))
    assert data == new_data


def mock_response(headers, data):
    return {
        'headers': headers,
        'body': {
            'string': json.dumps(data, sort_keys=True,
                                 separators=',:').encode('utf-8'),
        },
    }


def get_response_headers():
    return {
        'access-control-allow-origin': ['*'],
        'cache-control': ['private, no-cache, no-store, must-revalidate'],
        'connection': ['keep-alive'],
        'content-length': ['1'],  # will be updated
        'content-type': ['application/json; charset=UTF-8'],
        'date': ['Tue, 10 Nov 2015 20:32:22 GMT'],
        'expires': ['Sat, 01 Jan 2000 00:00:00 GMT'],
        'facebook-api-version': ['v2.0'],
        'pragma': ['no-cache'],
        'x-fb-debug': ['+pXMK8RrBwKIprCk9vFx66AM57N3rdXxbf3SkNBhupZ1NcNtzlREdocrrIOcRbQ4rb6IPT5XMqlHXFNOF6u3Mg=='],
        'x-fb-rev': ['2034042'],
        'x-fb-stats-contexts': ['api, V3'],
        'x-fb-trace-id': ['DQm+iTZ5TZS'],
    }


def get_simple_response_data():
    # https://graph.facebook.com/v2.4/<APP_SCOPED_SYSTEM_USER_ID>/access_tokens
    return {
        "access_token": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    }


def new_simple_response_data():
    return {
        "access_token": "XXX-08ad1422b56189a907f77ee2c7f3ea24"
    }


def get_paged_response_data():
    # https://graph.facebook.com/v2.4/me/accounts
    return {
        "data": [
            {
                "access_token": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
                "category": "Sports/Recreation/Activities",
                "category_list": [
                    {
                        "id": "176059775772759",
                        "name": "Golf Course"
                    }
                ],
                "name": "Foo Bar Golf Club",
                "id": "11111111111",
                "perms": [
                    "ADMINISTER",
                    "EDIT_PROFILE",
                    "CREATE_CONTENT",
                    "MODERATE_CONTENT",
                    "CREATE_ADS",
                    "BASIC_ADMIN"
                ]
            },
            {
                "access_token": "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
                "category": "Local Business",
                "category_list": [
                    {
                        "id": "2500",
                        "name": "Local Business"
                    }
                ],
                "name": "Aron's Test Biz",
                "id": "222222222222222",
                "perms": [
                    "ADMINISTER",
                    "EDIT_PROFILE",
                    "CREATE_CONTENT",
                    "MODERATE_CONTENT",
                    "CREATE_ADS",
                    "BASIC_ADMIN"
                ]
            },
            {
                "access_token": "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
                "category": "Spas/Beauty/Personal Care",
                "category_list": [
                    {
                        "id": "139225689474222",
                        "name": "Spa, Beauty & Personal Care"
                    }
                ],
                "name": "Foo Bar Beauty & Wellness",
                "id": "333333333333333",
                "perms": [
                    "ADMINISTER",
                    "EDIT_PROFILE",
                    "CREATE_CONTENT",
                    "MODERATE_CONTENT",
                    "CREATE_ADS",
                    "BASIC_ADMIN"
                ]
            },
            {
                "access_token": "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",
                "category": "Spas/Beauty/Personal Care",
                "category_list": [
                    {
                        "id": "199236533423806",
                        "name": "Beauty Salon"
                    }
                ],
                "name": "Foo Bar Strands",
                "id": "444444444444444",
                "perms": [
                    "ADMINISTER",
                    "EDIT_PROFILE",
                    "CREATE_CONTENT",
                    "MODERATE_CONTENT",
                    "CREATE_ADS",
                    "BASIC_ADMIN"
                ]
            }
        ],
        "paging": {
            "cursors": {
                "before": "NzgzMzE4NTg4MzkZD",
                "after": "NTUyODE4MjYxNDExMDk3"
            },
            "next": "https://graph.facebook.com/v2.4/555555555/accounts?access_token=EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE&limit=4&after=NTUyODE4MjYxNDExMDk3"
        }
    }

def new_paged_response_data():
    return {
        "data": [
            {
                "access_token": "XXX-08ad1422b56189a907f77ee2c7f3ea24",
                "category": "Sports/Recreation/Activities",
                "category_list": [
                    {
                        "id": "176059775772759",
                        "name": "Golf Course"
                    }
                ],
                "id": "11111111111",
                "name": "Foo Bar Golf Club",
                "perms": [
                    "ADMINISTER",
                    "EDIT_PROFILE",
                    "CREATE_CONTENT",
                    "MODERATE_CONTENT",
                    "CREATE_ADS",
                    "BASIC_ADMIN"
                ]
            },
            {
                "access_token": "XXX-871153402f713577851dd16e415cc4ca",
                "category": "Local Business",
                "category_list": [
                    {
                        "id": "2500",
                        "name": "Local Business"
                    }
                ],
                "id": "222222222222222",
                "name": "Aron's Test Biz",
                "perms": [
                    "ADMINISTER",
                    "EDIT_PROFILE",
                    "CREATE_CONTENT",
                    "MODERATE_CONTENT",
                    "CREATE_ADS",
                    "BASIC_ADMIN"
                ]
            },
            {
                "access_token": "XXX-d8ef23144cbbeff6face122ca35b2369",
                "category": "Spas/Beauty/Personal Care",
                "category_list": [
                    {
                        "id": "139225689474222",
                        "name": "Spa, Beauty & Personal Care"
                    }
                ],
                "id": "333333333333333",
                "name": "Foo Bar Beauty & Wellness",
                "perms": [
                    "ADMINISTER",
                    "EDIT_PROFILE",
                    "CREATE_CONTENT",
                    "MODERATE_CONTENT",
                    "CREATE_ADS",
                    "BASIC_ADMIN"
                ]
            },
            {
                "access_token": "XXX-0acd0c6197debb658e279f6b3ee7da47",
                "category": "Spas/Beauty/Personal Care",
                "category_list": [
                    {
                        "id": "199236533423806",
                        "name": "Beauty Salon"
                    }
                ],
                "id": "444444444444444",
                "name": "Foo Bar Strands",
                "perms": [
                    "ADMINISTER",
                    "EDIT_PROFILE",
                    "CREATE_CONTENT",
                    "MODERATE_CONTENT",
                    "CREATE_ADS",
                    "BASIC_ADMIN"
                ]
            }
        ],
        "paging": {
            "cursors": {
                "after": "NTUyODE4MjYxNDExMDk3",
                "before": "NzgzMzE4NTg4MzkZD"
            },
            "next": "https://graph.facebook.com/v2.4/555555555/accounts?access_token=XXX-ca7883a3a222faf30597933fb6b5649e&limit=4&after=NTUyODE4MjYxNDExMDk3"
        }
    }

def get_batch_response_data():
    return [
        {
            "code": 304,
            "headers": [
                {
                    "name": "Access-Control-Allow-Origin",
                    "value": "*"
                },
                {
                    "name": "Vary",
                    "value": "Accept-Encoding"
                },
                {
                    "name": "Pragma",
                    "value": "no-cache"
                },
                {
                    "name": "Cache-Control",
                    "value": "private, no-cache, no-store, must-revalidate"
                },
                {
                    "name": "Content-Type",
                    "value": "text/javascript; charset=UTF-8"
                },
                {
                    "name": "Facebook-API-Version",
                    "value": "v2.4"
                },
                {
                    "name": "Expires",
                    "value": "Sat, 01 Jan 2000 00:00:00 GMT"
                }
            ],
            "body": None
        },
        {
            "code": 200,
            "headers": [
                {
                    "name": "Access-Control-Allow-Origin",
                    "value": "*"
                },
                {
                    "name": "Expires",
                    "value": "Sat, 01 Jan 2000 00:00:00 GMT"
                },
                {
                    "name": "Cache-Control",
                    "value": "private, no-cache, no-store, must-revalidate"
                },
                {
                    "name": "Vary",
                    "value": "Accept-Encoding"
                },
                {
                    "name": "Pragma",
                    "value": "no-cache"
                },
                {
                    "name": "ETag",
                    "value": "\"1050253aec7b29caff644806927dabfa81406eee\""
                },
                {
                    "name": "Facebook-API-Version",
                    "value": "v2.4"
                },
                {
                    "name": "Content-Type",
                    "value": "text/javascript; charset=UTF-8"
                }
            ],
            "body": get_simple_response_data(),
        },
        {
            "code": 200,
            "headers": [
                {
                    "name": "Access-Control-Allow-Origin",
                    "value": "*"
                },
                {
                    "name": "Expires",
                    "value": "Sat, 01 Jan 2000 00:00:00 GMT"
                },
                {
                    "name": "Cache-Control",
                    "value": "private, no-cache, no-store, must-revalidate"
                },
                {
                    "name": "Vary",
                    "value": "Accept-Encoding"
                },
                {
                    "name": "Pragma",
                    "value": "no-cache"
                },
                {
                    "name": "ETag",
                    "value": "\"1050253aec7b29caff644806927dabfa81406eee\""
                },
                {
                    "name": "Facebook-API-Version",
                    "value": "v2.4"
                },
                {
                    "name": "Content-Type",
                    "value": "text/javascript; charset=UTF-8"
                }
            ],
            "body": get_paged_response_data(),
        },
    ]

def new_batch_response_data():
    return [
        {
            "code": 304,
            "headers": [
                {
                    "name": "Access-Control-Allow-Origin",
                    "value": "*"
                },
                {
                    "name": "Vary",
                    "value": "Accept-Encoding"
                },
                {
                    "name": "Pragma",
                    "value": "no-cache"
                },
                {
                    "name": "Cache-Control",
                    "value": "private, no-cache, no-store, must-revalidate"
                },
                {
                    "name": "Content-Type",
                    "value": "text/javascript; charset=UTF-8"
                },
                {
                    "name": "Facebook-API-Version",
                    "value": "v2.4"
                },
                {
                    "name": "Expires",
                    "value": "Sat, 01 Jan 2000 00:00:00 GMT"
                }
            ],
            "body": None
        },
        {
            "code": 200,
            "headers": [
                {
                    "name": "Access-Control-Allow-Origin",
                    "value": "*"
                },
                {
                    "name": "Expires",
                    "value": "Sat, 01 Jan 2000 00:00:00 GMT"
                },
                {
                    "name": "Cache-Control",
                    "value": "private, no-cache, no-store, must-revalidate"
                },
                {
                    "name": "Vary",
                    "value": "Accept-Encoding"
                },
                {
                    "name": "Pragma",
                    "value": "no-cache"
                },
                {
                    "name": "ETag",
                    "value": "\"1050253aec7b29caff644806927dabfa81406eee\""
                },
                {
                    "name": "Facebook-API-Version",
                    "value": "v2.4"
                },
                {
                    "name": "Content-Type",
                    "value": "text/javascript; charset=UTF-8"
                }
            ],
            "body": new_simple_response_data(),
        },
        {
            "code": 200,
            "headers": [
                {
                    "name": "Access-Control-Allow-Origin",
                    "value": "*"
                },
                {
                    "name": "Expires",
                    "value": "Sat, 01 Jan 2000 00:00:00 GMT"
                },
                {
                    "name": "Cache-Control",
                    "value": "private, no-cache, no-store, must-revalidate"
                },
                {
                    "name": "Vary",
                    "value": "Accept-Encoding"
                },
                {
                    "name": "Pragma",
                    "value": "no-cache"
                },
                {
                    "name": "ETag",
                    "value": "\"1050253aec7b29caff644806927dabfa81406eee\""
                },
                {
                    "name": "Facebook-API-Version",
                    "value": "v2.4"
                },
                {
                    "name": "Content-Type",
                    "value": "text/javascript; charset=UTF-8"
                }
            ],
            "body": new_paged_response_data(),
        },
    ]
