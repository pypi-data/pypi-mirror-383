"""Test the /mongo blueprint routes."""
# NOTE: modified subset of dservercore/tests/dataset_routes.py

import json

from . import compare_nested

from . import (
    grumpy_token,
    sleepy_token,
    dopey_token,
    noone_token,
)

def test_mongo_query_route(tmp_app_with_data):  # NOQA
    headers = dict(Authorization="Bearer " + grumpy_token)

    # first, just repeat all tests from test_dataset_search_route
    # without any raw query specified, query should behave equivalenty
    # to search.
    query = {}  # Everything.
    r = tmp_app_with_data.post(
        "/mongo/query",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 3

    r = tmp_app_with_data.post(
        "/mongo/query",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0

    r = tmp_app_with_data.post(
        "/mongo/query",
        headers=dict(Authorization="Bearer " + dopey_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    r = tmp_app_with_data.post(
        "/mongo/query",
        headers=dict(Authorization="Bearer " + noone_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    # try some direct mongo
    query = {
        'query': {
            'base_uri': 's3://snow-white',
            'readme.descripton': {'$regex': 'from queen'},
        }
    }
    r = tmp_app_with_data.post(
        "/mongo/query",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 2


def test_mongo_aggregate_route(tmp_app_with_data_and_relaxed_security):  # NOQA
    headers = dict(Authorization="Bearer " + grumpy_token)

    # first, just repeat all tests from test_dataset_search_route
    # without any aggregation specified, aggregate should behave equivalenty
    # to search.
    query = {}  # Everything.
    r = tmp_app_with_data_and_relaxed_security.post(
        "/mongo/aggregate",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 3

    r = tmp_app_with_data_and_relaxed_security.post(
        "/mongo/aggregate",
        headers=dict(Authorization="Bearer " + sleepy_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    assert len(json.loads(r.data.decode("utf-8"))) == 0

    r = tmp_app_with_data_and_relaxed_security.post(
        "/mongo/aggregate",
        headers=dict(Authorization="Bearer " + dopey_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    r = tmp_app_with_data_and_relaxed_security.post(
        "/mongo/aggregate",
        headers=dict(Authorization="Bearer " + noone_token),
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 401

    # try some direct aggregation
    query = {
        'aggregation': [
            {
                '$sort': {'base_uri': 1}
            }, {
                '$group':  {
                    '_id': '$name',
                    'count': {'$sum': 1},
                    'available_at': {'$push': '$base_uri'}
                }
            }, {
                '$project': {
                    'name': '$_id',
                    'count': True,
                    'available_at': True,
                    '_id': False,
                }
            }, {
                '$sort': {'name': 1}
            }
        ]
    }
    r = tmp_app_with_data_and_relaxed_security.post(
        "/mongo/aggregate",
        headers=headers,
        data=json.dumps(query),
        content_type="application/json"
    )
    assert r.status_code == 200
    expected_response = [
        {
            'available_at': ['s3://mr-men', 's3://snow-white'],
            'count': 2,
            'name': 'bad-apples'
        }, {
            'available_at': ['s3://snow-white'],
            'count': 1,
            'name': 'oranges'
        }
    ]
    response = json.loads(r.data.decode("utf-8"))
    assert compare_nested(response, expected_response)
