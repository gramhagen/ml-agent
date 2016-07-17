# -*- coding: utf-8 -*-
# pylint: disable=no-init
"""
SQLAlchemy object-relational mapping of deployed_models to DeployedModel object
"""

from sqlalchemy.types import INTEGER, FLOAT, TEXT, VARCHAR
from sqlalchemy import Column
from predict import db
from predict.enums import ModelStatus


class DeployedModel(db.Model):
    """
    DeployedModel class is a object-relational mapping of the deployed_models MySQL table
    DeployedModel objects are used throughout ML-Agent to represent, store, and operate on predictive models

    Args:
        model_id (str): unique string representing each model
        model_type (str): string defining type of model must be member of ModelType enum
        remote_path (str): remote location of model file to load 'protocol:///path/model.ext', supported protocols
            are ['http', 'ftp', 'hdfs', 'local']
        local_path (str): local path on server where model file is stored
        example (str): example feature vector to use for verifying model instantiation
        output (float): output prediction expected from model when using the example
        timestamp (int): epoch timestamp provided with model
        extras (str): additional arguments to use when instantiating the model
        info (str): additional metadata for the model
        status (str): status of model must be member of ModelStatus enum
    """

    __tablename__ = 'deployed_models'
    __table_args__ = {'extend_existing': True}

    model_id = Column('model_id', VARCHAR(100), primary_key=True, autoincrement=False)
    model_type = Column('model_type', VARCHAR(10), nullable=False)
    remote_path = Column('remote_path', VARCHAR(100), nullable=False)
    local_path = Column('local_path', VARCHAR(100), nullable=False, default='')
    example = Column('example', TEXT, nullable=False)
    output = Column('output', FLOAT, nullable=False)
    timestamp = Column('timestamp', INTEGER, nullable=False, default=0)
    extras = Column('extras', TEXT, nullable=False, default='')
    info = Column('info', TEXT, nullable=False, default='')
    status = Column('status', VARCHAR(10), nullable=False, default=ModelStatus.paused)

    def to_dict(self):
        """
        generate a dictionary representation of DeployedModel object (excluding magic sqlalchemy members)

        Returns:
            dict: DeployedModel attribute key-value pairs
        """

        return dict((k, self.__dict__[k]) for k in self.__dict__ if not k.startswith('_'))

    def clone(self):
        """
        generage a copy of all the attributes of the initial object

        Returns:
            DeployedModel: clone of original object
        """

        return DeployedModel(**self.to_dict())
