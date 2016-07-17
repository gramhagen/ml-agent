# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""
Test api calls
"""

import json
from flask import url_for
from tests.predict.conftest import get_vw_payload, get_vw_params


def test_model_ids_endpoints(accept_json, client):
    """
    hit model_ids endpoint and check for response codes
    """

    res = client.get(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 200
    assert res.mimetype == 'application/json'

    res = client.post(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 405

    res = client.put(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 405

    res = client.patch(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 405

    res = client.delete(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 405


def test_empty_model_ids(accept_json, client):
    """
    make sure model ids is empty to start
    """

    res = client.get(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 200
    assert res.data == '{"model_ids": []}'


def test_with_two_models(accept_json, client):
    """
    test creating two models and removing them one at a time
    """

    payload_1 = get_vw_payload(1)
    payload_2 = get_vw_payload(2)

    # test load model 1
    res = client.put(url_for('models', model_id=1), data=payload_1, headers=accept_json)
    assert res.status_code == 200
    assert json.loads(res.data) == dict(model_id='1', **get_vw_params(1))

    # test model 1 is in model list
    res = client.get(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 200
    assert res.data == '{"model_ids": ["1"]}'

    # test load model 2
    res = client.post(url_for('models', model_id=2), data=payload_2, headers=accept_json)
    assert res.status_code == 201
    assert json.loads(res.data) == dict(model_id='2', **get_vw_params(2))

    # test model 1 and 2 are in model list
    res = client.get(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 200
    assert res.data == '{"model_ids": ["1", "2"]}'

    # test model 1 and 2 are in model list
    res = client.get(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 200
    assert res.data == '{"model_ids": ["1", "2"]}'

    # test removal of model 2
    res = client.delete(url_for('models', model_id=2), headers=accept_json)
    assert res.status_code == 204

    # test model 1 is in model list
    res = client.get(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 200
    assert res.data == '{"model_ids": ["1"]}'

    # test removal of model 1
    res = client.delete(url_for('models', model_id=1), headers=accept_json)
    assert res.status_code == 204

    # test empty model list
    res = client.get(url_for('model_ids'), headers=accept_json)
    assert res.status_code == 200
    assert res.data == '{"model_ids": []}'
