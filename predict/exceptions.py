# -*- coding: utf-8 -*-
"""
Container for all custom exceptions and error handling
"""

from flask import current_app as app
from flask_restful import Api
from werkzeug.exceptions import BadRequest


class ErrorHandledApi(Api):
    """
    Extension of flask-restful Api class to add custom error handling
    """

    def handle_error(self, e):
        """
        override flask-restful handle_error method to add logging

        Args:
            e (Exception): error to handle

        Returns:
            json: string and error code
        """

        if issubclass(e.__class__, ApiException):
            app.logger.exception(e.to_string())
            return self.make_response(e.to_string(), e.status_code)
        elif isinstance(e, BadRequest):
            error_str = '[{code} {name}] {message}'.format(code=e.code, name=e.name, message=e.description)
            app.logger.error(error_str)
            return self.make_response(error_str, e.code)
        else:
            app.logger.exception(e.message)

        return super(self.__class__, self).handle_error(e)


class ApiException(Exception):
    """
    Generic exception generated during calls to prediction service APIs
    """

    def __init__(self, exception=None, name='Generic', message='error', status_code=500):
        """

        Args:
            exception (optional: Exception): exception object to use for name and message
            name (optional: str): name of exception, overrides exception name
            message (optional: str): exception body, overrides excpetion message
            status_code (optional: int): status code to return
        Returns:
            ApiException: exception object
        """

        if exception is not None:
            if name == 'Generic':
                name = type(exception).__name__
            if message == 'error':
                message = exception.message

        Exception.__init__(self, message)

        self.name = name
        self.message = message
        self.status_code = status_code

    def to_string(self):
        """
        write exception as string for logging

        Returns:
            str: exception string
        """

        return '[{code} {name}] {message}'.format(code=self.status_code, name=self.name, message=self.message)


class ModelNotFoundException(ApiException):
    """
    Exception class to use when model resource is not found
    """

    def __init__(self, model_id):
        name = 'Model Not Found'
        message = 'model {} could not be found'.format(model_id)
        super(self.__class__, self).__init__(name=name, message=message, status_code=404)


class ModelExistsException(ApiException):
    """
    Exception class to use when model creation is requests, but a model with the same id already exists
    """

    def __init__(self, model_id):
        name = 'Model Already Exists'
        message = 'model {} already exists'.format(model_id)
        super(self.__class__, self).__init__(name=name, message=message)


class ModelNotActive(ApiException):
    """
    Exception class to use when model resource is not active, but a request needing an active model is made
    """

    def __init__(self, model_id):
        name = 'Model Not Active'
        message = 'model {} is not active'.format(model_id)
        super(self.__class__, self).__init__(name=name, message=message)
