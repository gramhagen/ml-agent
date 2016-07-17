# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name, unused-argument
"""
Test scikit-learn model support
"""

import pytest
from predict.predictors.sklearn_predictor import SKLearnPredictor
from predict.models.deployed_model import DeployedModel
from tests.predict.conftest import get_sklearn_payload, generic_predictor
from predict.enums import ModelStatus
from tools.general import precision_compare


@pytest.fixture(scope='module')
def predictor(app):
    """
    test fixture for generating a sklearn predictor object

    Returns:
        object: sklearn predictor
    """

    return generic_predictor(model=DeployedModel(**get_sklearn_payload(1))).next()


def test_invalid_init():
    """
    confirm predictor won't initialize with invalid data
    """

    payload = get_sklearn_payload(1)
    payload['local_path'] = ' '

    # test invalid initialization
    with pytest.raises(Exception) as e:
        SKLearnPredictor(model=DeployedModel(**payload))
    assert e.value.message.startswith('could not load model file')


def test_sklearn_init(predictor):
    """
    confirm predictor will initialize with valid data
    """

    assert predictor.get_model().to_dict() == get_sklearn_payload(1)


def test_sklearn_batch_predict(predictor, sklearn_data):
    """
    test batch prediction
    """

    # test valid batch predictions
    expected = sklearn_data['predictions']
    outputs = predictor.predict(example=sklearn_data['examples'])

    print predictor.get_model()

    for pair in zip(expected, outputs):
        assert precision_compare(*pair)


def test_sklearn_predict(predictor, sklearn_data):
    """
    test predictions
    """

    for pair in zip(sklearn_data['predictions'], sklearn_data['examples']):
        assert precision_compare(pair[0], predictor.predict(example=[pair[1]]))


def test_sklearn_invalid_predict(predictor):
    """
    confirm predictor predicts as expected
    """

    # test empty prediction
    with pytest.raises(Exception) as e:
        predictor.predict(example='')
    assert e.value.message.startswith('invalid input')

    # test invalid examples
    with pytest.raises(Exception) as e:
        predictor.predict(example=['b'])
    assert e.value.message.startswith('prediction failed')

    with pytest.raises(Exception) as e:
        predictor.predict(example=['1'])
    assert e.value.message.startswith('prediction failed')

    with pytest.raises(Exception) as e:
        predictor.predict(example=['1,1'])
    assert e.value.message.startswith('prediction failed')


def test_sklearn_invalid_verify(app):
    """
    confirm predictor initialization fails if verification does not match
    """

    payload = get_sklearn_payload(1)
    example = payload['example']
    payload['example'] = '[0,0,0,0,0,0,0,0,0,0]'

    with pytest.raises(Exception) as e:
        SKLearnPredictor(model=DeployedModel(**payload))
    assert e.value.message.startswith('model verification failed')

    payload['example'] = None

    with pytest.raises(Exception) as e:
        SKLearnPredictor(model=DeployedModel(**payload))
    assert e.value.message.startswith('model verification failed')

    payload['example'] = example
    payload['output'] = 0

    with pytest.raises(Exception) as e:
        SKLearnPredictor(model=DeployedModel(**payload))
    assert e.value.message.startswith('model verification failed')


def test_sklearn_verify_on_load():
    """
    test model is not verified if flag is off
    """

    model = DeployedModel(**get_sklearn_payload(1))
    model.example = None
    model.output = None

    assert model.to_dict() == SKLearnPredictor(model=model, verify_on_load=False).get_model().to_dict()

def test_sklearn_load_paused():
    """
    test process is not loaded after predictor is started with paused state
    """

    model = DeployedModel(**get_sklearn_payload(1))
    model.status = ModelStatus.paused
    assert SKLearnPredictor(model=model, verify_on_load=False).process is None
