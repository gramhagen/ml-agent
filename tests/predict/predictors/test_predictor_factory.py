# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""
Test the predictor factory
"""

from predict.predictors.predictor_factory import make_predictor
from predict.models.deployed_model import DeployedModel
from predict.predictors.vw_predictor import VWPredictor
from predict.predictors.sklearn_predictor import SKLearnPredictor
from predict.exceptions import ApiException
from tests.predict.conftest import get_vw_payload, get_sklearn_payload
import pytest

vw_model = DeployedModel(**get_vw_payload(1))
sklearn_model = DeployedModel(**get_sklearn_payload(1))
bad_vw_model = DeployedModel(**get_vw_payload(1))
bad_vw_model.model_type = ''

# data provider tuples are:
#   model for factory to use when building a predictor
#   directly instantiated predictor
#   error type if error is expected
#   error message if error is expected
data = [(vw_model, VWPredictor(vw_model).get_model().to_dict(), None, ''),
        (sklearn_model, SKLearnPredictor(sklearn_model).get_model().to_dict(), None, ''),
        (bad_vw_model, None, ApiException, 'unknown model type')]


@pytest.mark.parametrize('model, predictor, error_type, error_msg', data)
def test_factory(app, model, predictor, error_type, error_msg):
    """
    test factory by building all supported predictor types
    """

    if error_type is None:
        factory_predictor = make_predictor(model=model).get_model().to_dict()
        assert predictor == factory_predictor
    else:
        with pytest.raises(error_type) as e:
            make_predictor(model=model)
        assert e.value.message.startswith(error_msg)

