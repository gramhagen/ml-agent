# -*- coding: utf-8 -*-
"""
Configuration environments available for this application\n
Environment variables, paths, logging, and configuration items are all setup here
each class corresponds to a different level of configuration, and the config dictionary provides access to each
"""

import os
import logging
from tempfile import NamedTemporaryFile


class Default(object):
    """
    base configuration class
    """

    # model options
    SKLEARN_SEPARATOR = ','
    MODEL_DIR = '/tmp/ml-agent_models'

    os.environ['JAVA_HOME'] = '/usr/java/latest'
    HADOOP = '/usr/local/hadoop/bin/hadoop'

    DEBUG = False

    # log options
    LOG_FMT = '[%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(funcName)s()] %(message)s'
    LOG_LEVEL = logging.DEBUG


class Production(Default):
    """
    production environment configuration
    """

    LOG_HANDLER = logging.FileHandler(filename='/var/log/research/ml-agent.log')
    LOG_LEVEL = logging.ERROR

    # READ-ONLY for now
    SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@mysql.server.com/ml-agent'


class Staging(Production):
    """
    staging environment configuration
    this uses MySQL but accesses the staging database
    """

    LOG_LEVEL = logging.DEBUG

    SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@mysql.server.com/ml-agent'


class Test(Default):
    """
    testing configuration environment
    uses sqllite database to support rapid unit-testing
    """

    LOG_HANDLER = logging.StreamHandler()

    TMP_DB = NamedTemporaryFile(delete=False).name
    SQLALCHEMY_ECHO = 'True'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(TMP_DB)
    MODEL_DIR = '/tmp/test_ml-agent_models'


config = {'prod': Production,
          'stage': Staging,
          'test': Test}
