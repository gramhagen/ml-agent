# -*- coding: utf-8 -*-
"""
Model ID API
"""

from flask_restful import Resource
from predict import mgmt


class ModelIDsApi(Resource):
    """
    API for requesting the ids for all models being managed by this service
    """

    @staticmethod
    def get():
        """
        provides list of model ids being managed by this service

        Returns:
            json: {'model_ids': (array(str))})
        """

        return {'model_ids': mgmt.get_model_ids()}
