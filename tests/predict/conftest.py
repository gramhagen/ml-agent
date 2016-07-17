# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
Contains general test fixtures
"""

import os
import pytest
from predict.app_factory import create_app
from predict.configurations import Test
from predict.predictors.predictor_factory import make_predictor
from predict.enums import ModelType, ModelStatus


@pytest.fixture(scope='session')
def app():
    """
    builds flask app using test environment

    Returns:
        object: flask app
    """

    return create_app(env='test')


def generic_predictor(model):
    """
    generator for generic predictor

    Args:
        model (DeployedModel): model for predictor to use

    Returns:
        object: predictor
    """

    predictor = make_predictor(model=model)

    yield predictor

    predictor.stop()

    # test predict on stopped model
    with pytest.raises(Exception) as e:
        predictor.predict(example='|')
    assert e.value.message == 'model process is not active'


@pytest.fixture(scope='session')
def vw_data():
    """
    generates data for vw predictor

    Returns:
        dict: dictionary of vw data representing a model with multiple examples and outputs
    """

    local_dir = '{}/data'.format(os.path.dirname(os.path.realpath(__file__)))
    data_file = '{}/vw_input.dat'.format(local_dir)
    output_file = '{}/vw_output.dat'.format(local_dir)

    data = dict()
    with open(data_file, 'r') as f:
        data['examples'] = f.readlines()
    with open(output_file, 'r') as f:
        data['predictions'] = [float(line.split(' ')[0]) for line in f]

    data['model_type'] = ModelType.vw
    data['local_path'] = '{}/vw.model'.format(local_dir)
    data['remote_path'] = 'local://{}'.format(data['local_path'])
    data['timestamp'] = 1429446926
    data['extras'] = '--loss_function=logistic'
    data['info'] = '{"cycle_id": 3619}'
    data['status'] = ModelStatus.active

    return data


def get_vw_payload(row):
    """
    generates data for creating one vw predictor

    Args:
        row (int): row of test data to use

    Returns:
        dict: dictionary of vw data representing a model
    """

    payload = vw_data().copy()

    payload['example'] = payload.pop('examples')[row]
    payload['output'] = payload.pop('predictions')[row]

    return payload


def get_vw_params(row):
    """
    generates data for expected result of creating one vw predictor (matching get_vw_payload)

    Args:
        row (int): row of test data to use

    Returns:
        dict: dictionary of vw data representing a instantiated predictor
    """

    payload = get_vw_payload(row)
    payload['local_path'] = '{dir}/{row}/vw.model'.format(dir=Test.MODEL_DIR, row=row)

    return payload


@pytest.fixture(scope='session')
def sklearn_data():
    """
    generates data for sklearn predictor

    Returns:
        dict: dictionary of sklearn data representing a model with multiple examples and outputs
    """

    local_dir = '{}/data'.format(os.path.dirname(os.path.realpath(__file__)))
    data_file = '{}/sklearn_input.dat'.format(local_dir)
    output_file = '{}/sklearn_output.dat'.format(local_dir)

    data = dict()
    with open(data_file, 'r') as f:
        data['examples'] = f.readlines()
    with open(output_file, 'r') as f:
        data['predictions'] = [float(line.split(' ')[0]) for line in f]

    data['model_type'] = ModelType.sklearn
    data['local_path'] = '{}/sklearn.model'.format(local_dir)
    data['remote_path'] = 'local://{}'.format(data['local_path'])
    data['timestamp'] = 1429446926
    data['extras'] = ''
    data['info'] = '{"cycle_id": 1234}'
    data['status'] = ModelStatus.active

    return data


def get_sklearn_payload(row):
    """
    generates data for creating one sklearn predictor

    Args:
        row (int): row of test data to use

    Returns:
        dict: dictionary of sklearn data representing a model
    """

    payload = sklearn_data().copy()

    payload['example'] = payload.pop('examples')[row]
    payload['output'] = payload.pop('predictions')[row]

    return payload
