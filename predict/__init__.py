# -*- coding: utf-8 -*-
"""
import flask extensions in the correct order
"""

# load SQLAlchemy extension
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# load predictor management object in memory
# this needs to happen after the db is built due to circular imports
from predict.predictors import management
mgmt = management

# load flask-restful api with custom error handling
from predict.exceptions import ErrorHandledApi
api = ErrorHandledApi()
