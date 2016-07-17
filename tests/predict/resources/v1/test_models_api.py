# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""
Test api calls
"""

import json
from flask import url_for
from tests.predict.conftest import get_vw_payload, get_vw_params
from predict.enums import ModelStatus
from tools.general import precision_compare
import os


def test_models_endpoint(accept_json, client):
    """
    hit models endpoint and check for response codes
    """

    res = client.get(url_for('models', model_id=0), headers=accept_json)
    assert res.status_code == 404
    assert res.mimetype == 'application/json'

    res = client.post(url_for('models', model_id=0), headers=accept_json)
    assert res.status_code == 400
    assert res.mimetype == 'application/json'

    res = client.put(url_for('models', model_id=0), headers=accept_json)
    assert res.status_code == 400
    assert res.mimetype == 'application/json'

    res = client.patch(url_for('models', model_id=0), headers=accept_json)
    assert res.status_code == 404
    assert res.mimetype == 'application/json'

    res = client.delete(url_for('models', model_id=0), headers=accept_json)
    assert res.status_code == 404
    assert res.mimetype == 'application/json'


def test_invalid_create(accept_json, client):
    """
    make sure invalid payload fails model creation
    """

    # load model with bad remote_path
    bad_payload = get_vw_payload(1)
    del bad_payload['remote_path']
    res = client.post(url_for('models', model_id=1), data=bad_payload, headers=accept_json)
    assert res.status_code == 400


def test_create_with_put(accept_json, client):
    """
    test creating a model with put (update)
    """

    # load model 3
    res = client.put(url_for('models', model_id=3), data=get_vw_payload(3), headers=accept_json)
    assert res.status_code == 200
    assert json.loads(res.data) == dict(model_id='3', **get_vw_params(3))

    # remove of model 3
    res = client.delete(url_for('models', model_id=3), headers=accept_json)
    assert res.status_code == 204


def test_with_one_model(accept_json, client):
    """
    test creating and showing model
    """

    # load model 1
    res = client.post(url_for('models', model_id=1), data=get_vw_payload(1), headers=accept_json)
    assert res.status_code == 201
    assert json.loads(res.data) == dict(model_id='1', **get_vw_params(1))

    # check error on loading another model 1
    res = client.post(url_for('models', model_id=1), data=get_vw_payload(1), headers=accept_json)
    assert res.status_code == 500

    # show model
    res = client.get(url_for('models', model_id=1), headers=accept_json)
    assert res.status_code == 200
    assert json.loads(res.data) == dict(model_id="1", **get_vw_params(1))

    # delete model
    res = client.delete(url_for('models', model_id=1), headers=accept_json)
    assert res.status_code == 204


def test_with_two_models(accept_json, client):
    """
    test creating two models and confirming predictions are correct for each
    """

    payload_1 = get_vw_payload(1)
    payload_2 = get_vw_payload(2)

    # load model 1
    res = client.post(url_for('models', model_id=1), data=payload_1, headers=accept_json)
    assert res.status_code == 201
    assert json.loads(res.data) == dict(model_id='1', **get_vw_params(1))

    # invalid predict on missing model 2
    res = client.post(url_for('predict', model_id=2), data={'example': payload_1['example']}, headers=accept_json)
    assert res.status_code == 404

    # load model 2
    res = client.post(url_for('models', model_id=2), data=payload_2, headers=accept_json)
    assert res.status_code == 201
    assert json.loads(res.data) == dict(model_id='2', **get_vw_params(2))

    # test prediction on model 1
    res = client.post(url_for('predict', model_id=1), data={'example': payload_1['example']}, headers=accept_json)
    assert res.status_code == 200
    assert precision_compare(payload_1['output'], json.loads(res.data)['prediction'])

    # test prediction on model 2
    res = client.post(url_for('predict', model_id=2), data={'example': payload_2['example']}, headers=accept_json)
    assert res.status_code == 200
    assert precision_compare(payload_2['output'], json.loads(res.data)['prediction'])

    # delete models
    res = client.delete(url_for('models', model_id=1), headers=accept_json)
    assert res.status_code == 204

    res = client.delete(url_for('models', model_id=2), headers=accept_json)
    assert res.status_code == 204


def test_model_update(accept_json, client):
    """
    test updating models
    """

    payload_1 = get_vw_payload(1)
    params_1 = get_vw_params(1)
    params_2 = get_vw_params(2)
    active = ModelStatus.active

    # load model 1
    res = client.post(url_for('models', model_id=1), data=payload_1, headers=accept_json)
    assert res.status_code == 201
    assert json.loads(res.data) == dict(model_id='1', **get_vw_params(1))

    # test full model update
    payload_1.update(example=params_2['example'], output=params_2['output'], status='paused')
    params_1.update(example=params_2['example'], output=params_2['output'], status='paused')

    res = client.put(url_for('models', model_id=1), data=payload_1, headers=accept_json)
    assert json.loads(res.data) == dict(model_id="1", **params_1)
    assert res.status_code == 200

    # test prediction on paused model
    res = client.post(url_for('predict', model_id=1), data={'example': params_1['example']}, headers=accept_json)
    assert res.status_code == 500

    # test partial model update
    params_1['status'] = active

    res = client.patch(url_for('models', model_id=1), data={'status': active}, headers=accept_json)
    assert json.loads(res.data) == dict(model_id="1", **params_1)
    assert res.status_code == 200

    # test prediction on model 1
    res = client.post(url_for('predict', model_id=1), data={'example': params_1['example']}, headers=accept_json)
    assert res.status_code == 200
    assert precision_compare(payload_1['output'], json.loads(res.data)['prediction'])

    # delete model
    res = client.delete(url_for('models', model_id=1), headers=accept_json)
    assert res.status_code == 204

    # test invalid model update
    del payload_1['status']
    res = client.patch(url_for('models', model_id=1), data=payload_1, headers=accept_json)
    assert res.status_code == 404


def test_bad_patch(accept_json, client):
    """
    test updating a model with bad data to make sure model files are managed correctly
    """

    payload_1 = get_vw_payload(1)
    params_1 = get_vw_params(1)

    # load model 1
    res = client.post(url_for('models', model_id=1), data=payload_1, headers=accept_json)
    assert res.status_code == 201
    assert json.loads(res.data) == dict(model_id='1', **get_vw_params(1))

    # test partial model update
    params_1['remote_path'] = '0{}'.format(params_1['remote_path'])

    res = client.patch(url_for('models', model_id=1), data={'remote_path': params_1['remote_path']}, headers=accept_json)
    assert res.status_code == 500

    # ensure original model file is intact and alone (no tmp files)
    assert os.listdir(os.path.dirname(params_1['local_path'])) == [os.path.basename(params_1['local_path'])]

    # test prediction on model 1
    res = client.post(url_for('predict', model_id=1), data={'example': params_1['example']}, headers=accept_json)
    assert res.status_code == 200
    assert precision_compare(payload_1['output'], json.loads(res.data)['prediction'])

    # delete model
    res = client.delete(url_for('models', model_id=1), headers=accept_json)
    assert res.status_code == 204


def test_no_verify(accept_json, client):
    """
    test loading models with empty example to skip verification on load
    """

    payload_1 = get_vw_payload(1)
    params_1 = get_vw_params(1)

    example = payload_1['example']
    output = payload_1['output']
    payload_1.update(example='', output=0)
    params_1.update(example='', output=0)

    # load test model
    res = client.put(url_for('models', model_id=1), data=payload_1, headers=accept_json)
    assert res.status_code == 200

    # test prediction on model
    res = client.post(url_for('predict', model_id=1), data={'example': example}, headers=accept_json)
    assert res.status_code == 200
    assert precision_compare(output, json.loads(res.data)['prediction'])

    # remove model
    res = client.delete(url_for('models', model_id=1), headers=accept_json)
    assert res.status_code == 204


def test_invalid_delete(accept_json, client):
    """
    test deleting models
    """

    res = client.delete(url_for('models', model_id=3), headers=accept_json)
    assert res.status_code == 404
