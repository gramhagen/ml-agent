# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name, unused-argument
"""
Test vowpal wabbit model support
"""

import math
import pytest
from predict.predictors.vw_predictor import VWPredictor
from predict.models.deployed_model import DeployedModel
from predict.enums import ModelStatus
from tests.predict.conftest import generic_predictor, get_vw_payload
from tools.general import precision_compare


@pytest.fixture(scope='module')
def predictor(app):
    """
    test fixture for generating a vw predictor object

    Returns:
        object: vw predictor
    """

    return generic_predictor(model=DeployedModel(**get_vw_payload(1))).next()


def test_invalid_init():
    """
    confirm predictor won't initialize with invalid data
    """

    payload = get_vw_payload(1)
    payload['local_path'] = ' '

    # test invalid initialization
    with pytest.raises(RuntimeError):
        VWPredictor(model=DeployedModel(**payload))


def test_vw_init(predictor):
    """
    confirm predictor will initialize with valid data
    """

    assert predictor.get_model().to_dict() == get_vw_payload(1)


def test_vw_batch_predict(predictor, vw_data):
    """
    test batch prediction
    """

    expected = vw_data['predictions']
    outputs = predictor.predict(example=vw_data['examples'])

    for pair in zip(expected, outputs):
        assert precision_compare(*pair)


def test_vw_predict(predictor, vw_data):
    """
    test predictions
    """

    for pair in zip(vw_data['predictions'], vw_data['examples']):
        assert precision_compare(pair[0], predictor.predict(example=[pair[1]])[0])


def test_vw_logit_predict():
    """
    confirm using link function gives the right prediction
    """

    payload = get_vw_payload(1)
    payload['extras'] += ' --link=logistic'
    payload['output'] = 1. / (1. + math.exp(-payload['output']))
    generic_predictor(model=DeployedModel(**payload)).next()


def test_vw_invalid_predict(predictor):
    """
    confirm predictor predicts as expected
    """

    # test empty prediction
    with pytest.raises(Exception) as e:
        predictor.predict(example='')
    assert e.value.message.startswith('invalid input')

    # test invalid examples
    with pytest.raises(Exception) as e:
        predictor.predict(example=['a'])
    assert e.value.message.startswith('invalid input')

    with pytest.raises(Exception) as e:
        predictor.predict(example=['1,1'])
    assert e.value.message.startswith('invalid input')

    with pytest.raises(Exception) as e:
        predictor.predict(example=['a a|'])
    assert e.value.message.startswith('invalid input')


def test_vw_process_failure(predictor):
    """
    confirm exception occurs if process is corrupted
    """

    process = predictor.process
    predictor.process = lambda: None

    with pytest.raises(Exception) as e:
        predictor.predict(example=['|1'])
    assert e.value.message.startswith('prediction failed')

    predictor.process = None
    with pytest.raises(Exception) as e:
        predictor.predict(example=['|1'])
    assert e.value.message.startswith('model process is not active')

    predictor.process = process


def test_invalid_verify(app):
    """
    confirm predictor initialization fails if verification does not match
    """

    payload = get_vw_payload(1)
    example = payload['example']
    payload['example'] = '|1'

    with pytest.raises(Exception) as e:
        VWPredictor(model=DeployedModel(**payload))
    assert e.value.message.startswith('model verification failed')

    payload['example'] = None

    with pytest.raises(Exception) as e:
        VWPredictor(model=DeployedModel(**payload))
    assert e.value.message.startswith('model verification failed')

    payload['example'] = example
    payload['output'] = 0

    with pytest.raises(Exception) as e:
        VWPredictor(model=DeployedModel(**payload))
    assert e.value.message.startswith('model verification failed')


def test_vw_verify_on_load():
    """
    test model is not verified if flag is off
    """

    model = DeployedModel(**get_vw_payload(1))
    model.example = '|1'
    model.output = None

    assert model.to_dict() == VWPredictor(model=model, verify_on_load=False).get_model().to_dict()


def test_vw_load_paused():
    """
    test process is not loaded after predictor is started with paused state
    """

    model = DeployedModel(**get_vw_payload(1))
    model.status = ModelStatus.paused
    assert VWPredictor(model=model, verify_on_load=False).process is None
