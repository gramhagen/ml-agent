# -*- coding: utf-8 -*-
"""
Scikit-learn predictor implementation\n
Models are expected to be implementations of a scikit-learn linear model and must support calling predict(X=example)\n
http://scikit-learn.org/stable/modules/classes.html#module-sklearn.linear_model
"""

from predict.predictors.base_predictor import BasePredictor
import numpy as np
import pickle


SKLEARN_SEPARATOR = ','


class SKLearnPredictor(BasePredictor):
    """
    Concrete class providing an interface to a scikit-learn model

    Attributes:
        sep (str): separator character to use when parsing the feature example strings
    """

    sep = None

    def __init__(self, model, sep=None, verify_on_load=True):
        """
        init for scikit-learn predictor, calls BasePredictor init then fills in specific attributes and loads model

        Args:
            model (DeployedModel): model to use for instantiating predictor
            sep (str): separator character to use when parsing the feature example strings

        Returns:
            SKLearnPredictor: SKLearnPredictor object
        """

        super(self.__class__, self).__init__(model=model)

        self.sep = sep or SKLEARN_SEPARATOR
        self.model_type = 'sklearn'

        self.load(verify_on_load=verify_on_load)

    def load(self, verify_on_load=True):
        """
        loads model file into memory if status is active
        model files are expected to be a pickled object of type sklearn.linear_model
        see http://scikit-learn.org/stable/modules/model_persistence.html
        """

        try:
            self.process = pickle.load(open(self.model.local_path, 'rb'))
        except Exception as e:
            raise Exception('could not load model file: {}'.format(e))

        super(self.__class__, self).load(verify_on_load=verify_on_load)

    def stop(self):
        """
        remove model from memory
        """

        self.process = None

    def predict(self, example):
        """
        provide prediction from feature example
        see http://scikit-learn.org/stable/modules/classes.html#module-sklearn.linear_model

        Args:
            example (arraylike(str)): example feature vector(s)

        Returns:
            arraylike(float) prediction(s)
        """

        assert self.can_predict(example=example)

        try:
            # convert array of strings to numpy array of arrays (of floats)
            example = [np.fromstring(x, sep=self.sep) for x in example]
            prediction = self.process.predict(X=example)
        except Exception as e:
            raise Exception('prediction failed: {err} on example {ex}.'.format(err=e, ex=example))

        return prediction
