# -*- coding: utf-8 -*-
"""
This provides the middle layer of managing predictive models (CRUD operations)
methods here provide an interface between the public APIs and predictor methods\n
The predictors dictionary is the in-memory singleton that houses all predictors\n
All file management is also handled here, removing that concern from the predictor layer
"""


from flask import current_app as app
from predict.models.deployed_model import DeployedModel
from predict.exceptions import ApiException, ModelNotFoundException, ModelNotActive
from predict import db
from predict.predictors.predictor_factory import make_predictor
from tools.general import run_process
import shutil
import os


predictors = dict()

MODEL_DIR = '/tmp/model_data'


def create_predictor(model, load_model=True):
    """
    instantiate a predictor, load it into dictionary for management and store it in database

    Args:
        model (DeployedModel): model for predictor to use
    """

    app.logger.debug('creating predictor: %s', model.to_dict())

    model_id = model.model_id

    if load_model:
        # create local copy of model file and update model
        model.local_path = load_model_file(model_id=model_id, remote_path=model.remote_path)

    # instantiate predictor
    predictor = make_predictor(model)

    app.logger.debug('instantiated predictor with model id: %s', model_id)

    # remove old model if it exists
    old_model = DeployedModel.query.filter_by(model_id=model_id).first()
    if old_model:
        db.session.delete(old_model)

    # insert new model
    db.session.add(model)
    db.session.commit()

    app.logger.debug('model id: %s stored in database', model_id)

    # the predictor is loaded into the dictionary last to ensure it is ready and verified before it can be accessed
    # this also provides for seamless updates to active predictors
    predictors[model_id] = predictor


def update_predictor(model):
    """
    update an existing predictor (keeps the same model id) or create new predictor if model id not found

    Args:
        model (DeployedModel): new model parameters to use
    """

    model_id = model.model_id

    # stop old predictor after new one has been loaded
    predictor = predictors.get(model_id, None)
    create_predictor(model)
    if predictor is not None:
        predictor.stop()


def patch_predictor(model_id, **kwargs):
    """
    patch parameters for an existing predictor (keeps the same model id)

    Args:
        model_id (str): unique string id for model
        kwargs (dict): parsed args mapping to fields in model object to update
    """

    if model_id not in predictors.keys():
        raise ModelNotFoundException(model_id)

    # stop old predictor after new one has been loaded
    predictor = predictors.get(model_id)
    model = get_model(model_id=model_id)

    # only reload model if the remote path has changed
    reload_model = 'remote_path' in kwargs
    for param, value in kwargs.iteritems():
        setattr(model, param, value)

    create_predictor(model, load_model=reload_model)
    predictor.stop()


def delete_predictor(model_id):
    """
    removes an existing predictor from management dictionary

    Args:
        model_id (str): model id for predictor to delete
    """

    if model_id not in predictors.keys():
        raise ModelNotFoundException(model_id)

    # remove model from list
    predictor = predictors.pop(model_id)
    model = predictor.get_model()

    try:
        predictor.stop()

        # clean up local files
        app.logger.debug('removing file: {}'.format(model.local_path))
        os.remove(model.local_path)

        local_dir = os.path.dirname(model.local_path)
        app.logger.debug('removing dir: {}'.format(local_dir))
        os.rmdir(local_dir)
    except Exception as e:
        raise ApiException(exception=e)
    finally:
        model = DeployedModel.query.filter_by(model_id=model_id).first()
        if model:
            db.session.delete(model)
            db.session.commit()


def get_model(model_id):
    """
    get model object from predictor with specified model id

    Args:
        model_id (str): model id for predictor

    Returns:
        DeployedModel: DeployedModel object
    """

    if model_id not in predictors.keys():
        raise ModelNotFoundException(model_id)

    return predictors[model_id].get_model()


def get_model_ids():
    """
    get model ids for all predictors in management dictionary

    Returns:
        array(str): model id keys for current predictors
    """

    return predictors.keys()


def get_model_dict(model_id):
    """
    returns a dictionary representation of model object for the specified predictor

    Args:
        model_id (str): model id for predictor
    Returns:
        dict: dictionary of model object from predictor with model id
    """

    return get_model(model_id=model_id).to_dict()


def predict(model_id, example):
    """
    wrapper for predictor's predict method

    Args:
        model_id (str): model id for predictor
        example (array(str)): example(s) for predictor to generate prediction(s)

    Returns:
        array(float): prediction(s)
    """

    if model_id not in predictors.keys():
        raise ModelNotFoundException(model_id)
    if not predictors[model_id].is_active():
        raise ModelNotActive(model_id)

    return predictors[model_id].predict(example=example)


def load_model_file(model_id, remote_path):
    """
    copy remote model file locally and provide the path of the local file

    Args:
        model_id (str): model id for predictor
        remote_path (str): remote location of model file to load 'protocol:///path/model.ext',
            supported protocols are ['http', 'ftp', 'hdfs', 'local']

    Returns:
        str: local path of model file loaded onto server
    """

    app.logger.debug('loading model id: %s from %s', model_id, remote_path)

    if model_id is None:
        raise ApiException(name='Invalid Input', message='missing model id')
    if remote_path is None:
        raise ApiException(name='Invalid Input', message='missing remote path: {}')

    # create model dir if needed
    created_dir = False
    model_base_dir = app.config.get('MODEL_DIR', MODEL_DIR)
    model_dir = '{dir}/{sub}'.format(dir=model_base_dir, sub=model_id)
    if not os.path.isdir(model_dir):
        app.logger.debug('creating model dir: %s', model_dir)
        os.makedirs(model_dir)
        created_dir = True

    app.logger.debug('using model dir: %s', model_dir)

    # remove file if exists
    renamed_file = None
    local_path = '{dir}/{file}'.format(dir=model_dir, file=os.path.basename(remote_path))
    tmp_local_path = None
    if os.path.isfile(local_path):
        app.logger.debug('removing existing model file: %s', local_path)
        tmp_local_path = '{}.tmp'.format(local_path)
        os.rename(local_path, tmp_local_path)
        renamed_file = tmp_local_path

    # copy model from remote path to local path
    try:
        if '://' not in remote_path:
            raise Exception('invalid remote path, expected [hdfs|http|ftp|local]://remote_dir/filename.ext')

        remote_info = remote_path.split('://')
        if remote_info[0] == 'hdfs':
            hadoop = app.config['HADOOP']
            cmd = '{hadoop} fs -copyToLocal {src} {dest}'.format(hadoop=hadoop, src=remote_info[1], dest=local_path)
        elif remote_info[0] == 'http' or remote_info[0] == 'ftp':
            cmd = 'wget -q {src} -O {dest}'.format(src=remote_info[1], dest=local_path)
        elif remote_info[0] == 'local':
            cmd = 'cp {src} {dest}'.format(src=remote_info[1], dest=local_path)
        elif remote_info[0] == 'scp':
            cmd = 'scp {src} {dest}'.format(src=remote_info[1], dest=local_path)
        else:
            msg = 'unknown transfer protocol {}, expected one of [hdfs|http|ftp|local]'
            raise Exception(msg.format(remote_info[0]))

        run_process(command=cmd, logger=app.logger)

        # confirm local path is valid and file was copied locally
        if not local_path or not os.path.isfile(local_path):
            raise Exception('local path not found')

        if renamed_file is not None:
            os.remove(tmp_local_path)
    except Exception as e:
        # if we made a mess clean it up
        if renamed_file is not None:
            os.rename(tmp_local_path, local_path)
        if created_dir:
            os.rmdir(model_dir)

        message = '{err} - copying remote path: {remote} to local path: {local}'
        raise ApiException(name='Invalid Input', message=message.format(err=e, remote=remote_path, local=local_path))

    app.logger.debug('loaded model id: %s from remote path: %s to local path %s', model_id, remote_path, local_path)

    return local_path


def create_predictors():
    """
    create all predictors in database, this will overwrite any
    predictors in the management dictionary with the same model id
    """

    map(create_predictor, DeployedModel.query.all())


def reload_predictor(model_id):
    """
    reload a predictor already existing in the management dictionary

    Args:
        model_id (str): model id of predictor to reload
    """

    update_predictor(model=get_model(model_id=model_id))


def reload_predictors():
    """
    reload all predictors in management dictionary
    """

    map(reload_predictor, predictors.keys())


def clear_model_dir():
    """
    clear model directory and load all predictors from database
    """

    try:
        model_dir = app.config.get('MODEL_DIR', None)
        shutil.rmtree(model_dir)
    except Exception as e:
        app.logger.error('error: %s', e)
        app.logger.error('could not clear model directory %s', app.config['MODEL_DIR'])


def startup():
    """ start management layer """

    clear_model_dir()
    create_predictors()


def shutdown():
    """
    delete all predictors in management dictionary
    """

    map(delete_predictor, predictors.keys())
