# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""
Test management layer
"""

import pytest
import shutil
import os
from time import time
from predict.models.deployed_model import DeployedModel
from predict import mgmt, db
from predict.exceptions import ApiException
from tests.predict.conftest import get_vw_params


load_model_data = [(None, ' ', 'missing model id'),
                   (10, None, 'missing remote path'),
                   (11, '', 'invalid remote path'),
                   (12, 'blarg', 'invalid remote path'),
                   (13, 'blrg:///wtf/foo.bar', 'unknown transfer protocol'),
                   (14, 'hdfs://', None),
                   (15, 'http://', None),
                   (16, 'ftp://', None),
                   (17, 'local://', None),
                   (18, 'scp://', None),
                   (19, 'scp://', 'local path not found')]


@pytest.mark.parametrize('model_id, remote_path, error', load_model_data)
def test_load_model_file(app, tmpdir, monkeypatch, model_id, remote_path, error):
    """
    test the load model method
    """

    # create tempororay model file
    filename = 'tmp.model'
    full_path = tmpdir.mkdir('ml-agent_fake_models').join(filename)
    full_path.write('test')

    # assign local source and destination files
    src = str(full_path)
    dest = '{dir}/{id}/{filename}'.format(dir=app.config['MODEL_DIR'], id=model_id, filename=filename)

    # define command to execute based on protocol in remote path
    if remote_path:
        remote_path += src
        if remote_path.startswith('hdfs'):
            cmd = '{cmd} fs -copyToLocal {src} {dest}'.format(cmd=app.config['HADOOP'], src=src, dest=dest)
        elif remote_path.startswith('http') or remote_path.startswith('ftp'):
            cmd = 'wget -q {src} -O {dest}'.format(src=src, dest=dest)
        elif remote_path.startswith('local'):
            cmd = 'cp {src} {dest}'.format(src=src, dest=dest)
        elif remote_path.startswith('scp'):
            cmd = 'scp {src} {dest}'.format(src=src, dest=dest)

    def mock_run_process(command, logger=None):
        """
        mock run_process to check if correct command is being issued to shell
        then manually copy src file to dest, and return dest path
        """

        assert command == cmd
        if not error:
            shutil.copy(src, dest)
        return dest

    # need to patch mgmt's run_process method with mock_run_process
    monkeypatch.setattr(mgmt, 'run_process', mock_run_process)

    try:
        local_path = mgmt.load_model_file(model_id=model_id, remote_path=remote_path)
        assert local_path == dest
        shutil.rmtree(os.path.dirname(dest))
    except ApiException as e:
        # if error was provided with test data ensure correct error resulted
        if error:
            assert e.message.startswith(error)
        else:
            raise


def test_load_from_db(app):
    """
    test the capability to reload models from the database
    """

    model_1_dict = dict(model_id='1', **get_vw_params(1))
    model_2_dict = dict(model_id='2', **get_vw_params(2))

    # clear db
    db.drop_all()
    db.create_all()

    # add models to database
    model_1 = DeployedModel(**model_1_dict)
    model_2 = DeployedModel(**model_2_dict)
    db.session.add(model_1)
    db.session.add(model_2)
    db.session.commit()

    # confirm they exist in database
    model_1 = DeployedModel.query.filter(DeployedModel.model_id == 1).first()
    model_2 = DeployedModel.query.filter(DeployedModel.model_id == 2).first()
    assert model_1.to_dict() == model_1_dict
    assert model_2.to_dict() == model_2_dict

    # test initialization and loading models from database
    mgmt.create_predictors()
    assert mgmt.get_model_ids() == ['1', '2']
    assert mgmt.get_model_dict('1') == model_1_dict
    assert mgmt.get_model_dict('2') == model_2_dict

    # test that nothing has changed after reloading
    mgmt.reload_predictors()
    assert mgmt.get_model_ids() == ['1', '2']
    assert mgmt.get_model_dict('1') == model_1_dict
    assert mgmt.get_model_dict('2') == model_2_dict


def test_model_deletion(app):
    """
    test model deletion
    """

    mgmt.delete_predictor('2')
    assert '2' not in mgmt.get_model_ids()

    # test exception in model deletion
    model_2 = DeployedModel(model_id='2', **get_vw_params(2))
    mgmt.create_predictor(model_2)

    tmp_local_path = '{}.tmp'.format(model_2.local_path)
    shutil.copy(model_2.local_path, tmp_local_path)

    with pytest.raises(ApiException) as e:
        mgmt.delete_predictor('2')
    assert e.value.status_code == 500
    assert '2' not in mgmt.get_model_ids()

    shutil.rmtree(os.path.dirname(tmp_local_path))


def test_shutdown(app):
    """
    test that models are not accessible after shutdown
    """

    mgmt.shutdown()
    assert mgmt.get_model_ids() == []
    with pytest.raises(Exception) as e:
        mgmt.get_model_dict('1')
    assert e.value.message == 'model 1 could not be found'

    assert not DeployedModel.query.all()


def test_clear_model_dir(app):
    """
    test clearing model directory
    """

    model_dir = app.config['MODEL_DIR']
    new_model_dir = '{dir}_{ts}'.format(dir=model_dir, ts=int(time()))
    os.mkdir(new_model_dir)

    assert os.path.isdir(new_model_dir)

    app.config['MODEL_DIR'] = new_model_dir
    mgmt.clear_model_dir()

    assert not os.path.isdir(new_model_dir)

    app.config['MODEL_DIR'] = model_dir


def test_clear_bad_model_dir(app, caplog):
    """
    test clearing model directory
    """

    model_dir = app.config['MODEL_DIR']
    new_model_dir = '{dir}_{ts}'.format(dir=model_dir, ts=int(time()))

    assert not os.path.isdir(new_model_dir)

    app.config['MODEL_DIR'] = new_model_dir

    mgmt.clear_model_dir()

    assert 'error: [Errno 2] No such file or directory' in caplog.text()

    app.config['MODEL_DIR'] = model_dir
