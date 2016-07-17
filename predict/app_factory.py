"""
Flask application factory
"""

import logging

from flask import Flask

from predict import db, mgmt, api
from predict.configurations import config
from predict.resources.v1.model_ids_api import ModelIDsApi
from predict.resources.v1.models_api import ModelsApi
from predict.resources.v1.predict_api import PredictApi
from docs.views import doc_app


def create_app(env='stage'):
    """
    builds flask app

    Args:
        env (str): configuration environment to use see config/configurations.py

    Returns:
        (object) flask application
    """
    cfg = config[env]

    # application factory
    app = Flask(__name__)
    app.config.from_object(cfg)

    # add logger defined from configuration
    app.config['LOG_HANDLER'].setFormatter(fmt=logging.Formatter(app.config['LOG_FMT']))
    app.logger.handlers = [app.config['LOG_HANDLER']]
    app.logger.setLevel(app.config['LOG_LEVEL'])

    # sqlalchemy database
    db.init_app(app)

    # create tables if using a tmp db
    if app.config.get('TMP_DB', False):
        db.create_all(app=app)

    # model manager
    with app.app_context():
        mgmt.startup()

    # add api resources
    api.add_resource(ModelIDsApi, '/v1/models', endpoint='model_ids')
    api.add_resource(ModelsApi, '/v1/models/<model_id>', endpoint='models')
    api.add_resource(PredictApi, '/v1/predict/<model_id>', endpoint='predict')
    api.init_app(app)

    app.logger.debug('creating predict app with %s configuration', env)

    app.register_blueprint(doc_app)

    return app
