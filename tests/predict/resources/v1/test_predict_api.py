# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""
Test api calls
"""

import json
from flask import url_for
from tests.predict.conftest import get_vw_payload, get_vw_params
from tools.general import precision_compare


def test_predict_endpoint(accept_json, client):
    """
    hit predict endpoint and check for response codes
    """

    res = client.get(url_for('predict', model_id=0), data={'example': ''}, headers=accept_json)
    assert res.status_code == 405

    res = client.post(url_for('predict', model_id=0), data={'example': ''}, headers=accept_json)
    assert res.status_code == 404
    assert res.mimetype == 'application/json'

    res = client.put(url_for('predict', model_id=0), data={'example': ''}, headers=accept_json)
    assert res.status_code == 405

    res = client.patch(url_for('predict', model_id=0), data={'example': ''}, headers=accept_json)
    assert res.status_code == 405

    res = client.delete(url_for('predict', model_id=0), data={'example': ''}, headers=accept_json)
    assert res.status_code == 405


def test_invalid_predict(accept_json, client):
    """
    make sure predict on missing model fails
    """

    res = client.post(url_for('predict', model_id=1), data={'example': get_vw_params(1)['example']}, headers=accept_json)
    assert res.status_code == 404


def test_batch_prediction(accept_json, client, vw_data):
    """
    test batch prediction
    """

    # load model 1
    res = client.post(url_for('models', model_id=1), data=get_vw_payload(1), headers=accept_json)
    assert res.status_code == 201
    assert json.loads(res.data) == dict(model_id='1', **get_vw_params(1))

    # test batch prediction on model 1
    data = {'example': vw_data['examples']}
    res = client.post(url_for('predict', model_id=1), data=data, headers=accept_json)
    assert res.status_code == 200
    for pair in zip(vw_data['predictions'], json.loads(res.data)['prediction']):
        assert precision_compare(pair[0], pair[1])

    # delete model
    res = client.delete(url_for('models', model_id=1), headers=accept_json)
    assert res.status_code == 204
