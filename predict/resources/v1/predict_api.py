# -*- coding: utf-8 -*-
"""
Predict APIs
"""

from flask_restful import Resource, reqparse
from predict.exceptions import ApiException, ModelNotFoundException
from predict import mgmt


class PredictApi(Resource):
    """
    API for generating predictions from loaded models
    """

    @staticmethod
    def post(model_id):
        """
        provide feature example(s) and get prediction(s).
        body must only contain one example argument.
        if examples is an array predictions are provided in the same order

        Args:
            model_id (str): model id of predictor to use
            example (str) or array(str): feature example(s) for predictions


        Returns:
            json: dictionary {'prediction': float}, or {'prediction': (array(float))} if using multiple examples
        """

        parser = reqparse.RequestParser()
        parser.add_argument('example', required=True, type=str, action='append', help='feature example for prediction')
        pargs = parser.parse_args(strict=True)

        try:
            prediction = mgmt.predict(model_id=model_id, example=pargs.example)
            return {'prediction': prediction} if len(prediction) > 1 else {'prediction': prediction[0]}
        except ModelNotFoundException as e:
            raise e
        except Exception as e:
            raise ApiException(exception=e)
