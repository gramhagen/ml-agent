# -*- coding: utf-8 -*-
"""
Stress testing model building
"""


import json
from locust import HttpLocust, TaskSet, task
from tests.predict.conftest import get_vw_payload
from predict.configurations import config
import os


MAX_MODELS = 1000
MODELS_API_URL = '/v1/models'
PAYLOAD = get_vw_payload(1)
HEADERS = {'Content-type': 'application/json'}


class BuildModels(TaskSet):
    """ use this class to evaluate speed and capacity for building models"""

    model_id = 0

    @task
    def add_model(self):
        """ check that model built was what was expected """

        local_path = PAYLOAD['local_path']
        new_path = '{dir}/{model}'.format(dir=config['test'].MODEL_DIR, model=self.model_id)
        expected = dict(model_id=str(self.model_id), **PAYLOAD)
        expected['local_path'] = local_path.replace(os.path.dirname(local_path), new_path)
        expected = json.dumps(expected)

        addr = '{models}/{id}'.format(models=MODELS_API_URL, id=self.model_id)
        with self.client.put(addr, data=json.dumps(PAYLOAD), catch_response=True, headers=HEADERS) as response:
            if response.content != expected:
                err = 'invalid response - expected: {exp}, actual: {act}'.format(exp=expected, act=response.content)
                response.failure(err)

        # don't create more than max models
        self.model_id = (self.model_id + 1) % MAX_MODELS


class WebsiteUser(HttpLocust):
    """ set up a locust tasked with building models """

    task_set = BuildModels
    min_wait = 2000
    max_wait = 5000
