# -*- coding: utf-8 -*-
"""
Factory for building predictors
"""

from flask import current_app as app
from predict.predictors.vw_predictor import VWPredictor
from predict.predictors.sklearn_predictor import SKLearnPredictor
from predict.exceptions import ApiException
from predict.enums import ModelType


def make_predictor(model):
    """
    Factory to build predictor based on model type provided

    Args:
        model (DeployedModel): model to use when instantiating a predictor

    Returns:
        BasePredictor Child: instantiated predictor object
    """

    verify = False if model.example == '' else True

    if model.model_type == ModelType.vw:
        return VWPredictor(model=model, verify_on_load=verify)
    elif model.model_type == ModelType.sklearn:
        return SKLearnPredictor(model=model, sep=app.config.get('SKLEARN_SEPARATOR', None), verify_on_load=verify)
    else:
        raise ApiException(name='Invalid Input', message='unknown model type: {type}'.format(type=model.model_type))
