# -*- coding: utf-8 -*-
"""
Test base predictor class
"""

import pytest
from predict.predictors.base_predictor import BasePredictor


# pylint: disable=super-init-not-called
class TestPredictor(BasePredictor):
    """
    test creating a new predictor class with BasePredictor as a parent
    """

    def __init__(self, model):
        pass

    def load(self, verify_on_load=True):
        super(self.__class__, self).load()

    def stop(self):
        super(self.__class__, self).stop()

    def predict(self, example=''):
        super(self.__class__, self).predict(example)


# pylint: disable=abstract-class-instantiated
def test_construction():
    """
    test construction of child class of BasePredictor
    """

    model = lambda: None
    assert isinstance(TestPredictor(model=model), TestPredictor)

    # pylint: disable=abstract-method
    class InvalidPredictor(BasePredictor):
        """ invalid predictor class """
        def __init__(self, model):
            pass

    with pytest.raises(TypeError) as e:
        InvalidPredictor(model=model)
    assert e.value.message.startswith("Can't instantiate abstract class")


def test_abstract_methods():
    """
    ensure abstract methods are respected
    """

    with pytest.raises(TypeError) as e:
        BasePredictor(model=None)  # pylint: disable=abstract-class-instantiated
    assert e.value.message.startswith("Can't instantiate abstract class BasePredictor")

    predictor = TestPredictor(model=None)

    with pytest.raises(Exception) as e:
        predictor.stop()
    assert e.value.message == 'cannot call abstract stop method in base predictor class'

    with pytest.raises(Exception) as e:
        predictor.predict()
    assert e.value.message == 'cannot call abstract predict method in base predictor class'

