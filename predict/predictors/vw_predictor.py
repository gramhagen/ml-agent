# -*- coding: utf-8 -*-
"""
Vowpal wabbit predictor implementation\n
This will create a subprocess running vowpal wabbit binary installed on the local machine\n
Model versions should match the version of vw installed on the machine (this is not verified at run-time)\n
https://github.com/JohnLangford/vowpal_wabbit/wiki
"""

from predict.predictors.base_predictor import BasePredictor
from vowpalwabbit import pyvw
import re


valid_regex = re.compile(r"(([-0-9\.]+ )?([-0-9\.]+ )?([\S^\|]+|('[\S^\|]+ ))?\|.*)")


class VWPredictor(BasePredictor):
    """
    Concrete class providing interface for a Vowpal Wabbit model
    """

    def __init__(self, model, verify_on_load=True):
        """
        init for vowpal wabbit predictor, calls BasePredictor init then fills in specific attributes and loads model.
        uses python binding to c++ executable to make predictions.
        model.extras can provide addition arguments to vw:
        see https://github.com/JohnLangford/vowpal_wabbit/wiki/Command-line-arguments

        Args:
            model (DeployedModel): model to use for instantiating predictor

        Returns:
            VWPredictor: VWPredictor object
        """

        super(self.__class__, self).__init__(model=model)

        self.model_type = 'vw'

        self.command = '-i {path} --quiet'.format(path=self.model.local_path)
        if self.model.extras:
            # don't allow duplicate quiets in extras
            extras = self.model.extras.replace('--quiet', '')
            self.command += ' {}'.format(extras)

        self.load(verify_on_load=verify_on_load)

    def load(self, verify_on_load=True):
        """
        loads model file into memory (as a vw sub-process)
        verify model first, then stop process if status is not active

        Args:
            verify_on_load (bool): flag to call verify when loading a model
        """

        self.process = pyvw.vw(self.command)

        super(self.__class__, self).load(verify_on_load=verify_on_load)

    def stop(self):
        """
        stops vw from processing
        """

        if self.is_active():
            self.process.finish()
        self.process = None

    def predict(self, example):
        """
        provide prediction from example, each example string must match vw input format
        see https://github.com/JohnLangford/vowpal_wabbit/wiki/Input-format

        Args:
            example (arraylike(str)): example feature vector(s)

        Returns:
            arraylike(float): prediction(s)
        """

        assert self.can_predict(example=example)

        prediction = []
        for row in example:
            row = row.strip().encode('ascii', 'ignore')
            if not self.validate(row):
                raise Exception('invalid input: {}'.format(row))
            try:
                ex = self.process.example(row)
                ex.set_test_only(True)
                ex.learn()
                prediction.append(ex.get_simplelabel_prediction())
            except Exception as e:
                raise Exception('prediction failed: {err} on example {ex}.'.format(err=e, ex=row))

        return prediction

    @staticmethod
    def validate(example):
        """
        match regular expression defining valid vw input format

        Args:
            example (str): input example

        Returns:
            bool: True if input is valid vw format, False otherwise
        """

        match = valid_regex.match(example)
        return match and match.group(0) == example
