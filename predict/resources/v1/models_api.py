# -*- coding: utf-8 -*-
"""
Models APIs
"""

from flask import current_app as app
from flask_restful import Resource, reqparse
from predict.exceptions import ModelExistsException
from predict import mgmt
from predict.enums import ModelType, ModelStatus
from predict.models.deployed_model import DeployedModel
from time import time


MODEL_TYPES = ModelType.values()
MODEL_STATUSES = ModelStatus.values()


class ModelsApi(Resource):
    """
    API for CRUD operations on models
    """

    @staticmethod
    def get(model_id):
        """
        returns parameters of model

        Args:
            model_id (str): requested model id

        Returns:
            json: dict of model
        """

        return mgmt.get_model_dict(model_id)

    @staticmethod
    def post(model_id):
        """
        create new predictor for the given model parameters.
        body of request must contain all of the required arguments (excluding model_id) and may contain any of (but no
        more than) the optional arguments.

        Args:
            model_id (str): unique string of id for model
            model_type (str): type of model must be valid member of ModelType enum
            local_path (optional, str): local path of model file - this is only used internally
            remote_path (str): remote location of model file to load 'protocol:///path/model.ext',
                supported protocols are ['http', 'scp', 'hdfs', 'local']
            example (str): example feature vector to use for verifying model instantiation, using an empty string
                disables validation of the model on load
            output (float): output prediction expected from model when using the example
            timestamp (optional, int): epoch timestamp provided with model, defaults to current timestamp
            extras (optional, str): additional arguments to use when instantiating the model
            info (optional, str): additional information on the model
            status (optional, str): status of model must be valid member of ModelStatus enum, default 'paused'

        Returns:
            json: dictionary loaded model
        """

        if model_id in mgmt.get_model_ids():
            raise ModelExistsException(model_id)

        app.logger.debug('post model for model id: %s', model_id)

        parser = reqparse.RequestParser()
        parser.add_argument('model_type', required=True, type=str, choices=MODEL_TYPES, help='type of model')
        parser.add_argument('local_path', type=str, help='local path to model')
        parser.add_argument('remote_path', required=True, type=str, help='remote path to model')
        parser.add_argument('example', required=True, type=str, help='example feature vector for model')
        parser.add_argument('output', required=True, type=float, help='expected output of model')
        parser.add_argument('timestamp', type=int, default=int(time()), help='epoch timestamp when model was trained')
        parser.add_argument('extras', type=str, default='', help='extra parameters to use with model')
        parser.add_argument('info', type=str, default='', help='information on the model')
        parser.add_argument('status', type=str, choices=MODEL_STATUSES, default=ModelStatus.paused,
                            help='model status')
        pargs = parser.parse_args(strict=True)

        # instantiate model
        mgmt.create_predictor(model=DeployedModel(model_id=model_id, **pargs))

        return mgmt.get_model_dict(model_id), 201

    @staticmethod
    def put(model_id):
        """
        replace or create a predictor with the given model parameters.
        body of request must contain all of the required arguments (excluding model_id) and may contain any of (but
        no more than) the optional arguments.

        Args:
            model_id (str): unique string id for predictor to replace
            model_type (str): type of model must be valid member of ModelType enum
            local_path (optional, str): local path of model file - this is only used internally
            remote_path (str): remote location of model file to load 'protocol:///path/model.ext',
                supported protocols are ['http', 'scp', 'hdfs', 'local']
            example (str): example feature vector to use for verifying model instantiation, using an empty string
                disables validation of the model on load
            output (float): output prediction expected from model when using the example
            timestamp (optional, int): epoch timestamp provided with model, defaults to current timestamp
            extras (optional, str): additional arguments to use when instantiating the model
            info (optional, str): additional information on the model
            status (optional, str): status of model must be valid member of ModelStatus enum, default 'paused'

        Returns:
            json: dictionary of updated model
        """

        app.logger.debug('put model for model id: %s', model_id)

        parser = reqparse.RequestParser()
        parser.add_argument('model_type', required=True, type=str, choices=MODEL_TYPES, help='type of model')
        parser.add_argument('local_path', type=str, help='local path to model')
        parser.add_argument('remote_path', required=True, type=str, help='remote path to model')
        parser.add_argument('example', required=True, type=str, help='example feature vector for model')
        parser.add_argument('output', required=True, type=float, help='expected output of model')
        parser.add_argument('timestamp', type=int, default=int(time()), help='epoch timestamp when model was trained')
        parser.add_argument('extras', type=str, default='', help='extra parameters to use with model')
        parser.add_argument('info', type=str, default='', help='information on the model')
        parser.add_argument('status', type=str, choices=MODEL_STATUSES, default=ModelStatus.paused,
                            help='model status')
        pargs = parser.parse_args(strict=True)

        mgmt.update_predictor(model=DeployedModel(model_id=model_id, **pargs))

        return mgmt.get_model_dict(model_id), 200

    @staticmethod
    def patch(model_id):
        """
        update a predictor with the given model parameters.
        body of request can contain any of (but no more than) the following arguments (excluding model_id).
        any excluded parameters will not be changed from the existing model

        Args:
            model_id (str): unique string id for model
            model_type (str): type of model must be valid member of ModelType enum
            local_path (optional, str): local path of model file - this is only used internally
            remote_path (optional, str): remote location of model file to load 'protocol:///path/model.ext',
                supported protocols are ['http', 'scp', 'hdfs', 'local']
            example (optional, str): example feature vector to use for verifying model instantiation
            output (optional, float): output prediction expected from model when using the example
            timestamp (optional, int): epoch timestamp provided with model
            extras (optional, str): additional arguments to use when instantiating the model
            info (optional, str): additional information on the model
            status (optional, str): status of model must be valid member of ModelStatus enum

        Returns:
            json: dictionary of updated model
        """

        app.logger.debug('patch model for model id: %s', model_id)

        parser = reqparse.RequestParser()
        parser.add_argument('model_type', type=str, choices=MODEL_TYPES, help='type of model')
        parser.add_argument('local_path', type=str, help='local path to model')
        parser.add_argument('remote_path', type=str, help='remote path to model')
        parser.add_argument('example', type=str, help='example feature vector for model')
        parser.add_argument('output', type=float, help='expected output of model')
        parser.add_argument('timestamp', type=int, help='epoch timestamp when model was trained')
        parser.add_argument('extras', type=str, help='extra parameters to use with model')
        parser.add_argument('info', type=str, help='information on the model')
        parser.add_argument('status', type=str, choices=MODEL_STATUSES, help='model status')
        pargs = parser.parse_args(strict=False)

        kwargs = dict((k, pargs[k]) for k in pargs if pargs[k] is not None)
        mgmt.patch_predictor(model_id, **kwargs)

        return mgmt.get_model_dict(model_id), 200

    @staticmethod
    def delete(model_id):
        """
        deletes a predictor

        Args:
            model_id (str): unique string id for model

        Returns:
            str: ''
        """

        app.logger.debug('delete model for model id: %s', model_id)
        mgmt.delete_predictor(model_id=model_id)

        return '', 204
