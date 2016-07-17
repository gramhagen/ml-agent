# -*- coding: utf-8 -*-
"""
Stress testing prediction speed
"""


import json
from locust import HttpLocust, TaskSet, task
from tests.predict.conftest import get_vw_payload
from tools.general import precision_compare


MAX_REQUESTERS = 1000
MODEL_ID = '1'
PREDICT_URL = '/v1/predict/{}'.format(MODEL_ID)
HEADERS = {'Content-type': 'application/json'}
PAYLOAD = get_vw_payload(1)


class Predict(TaskSet):
    """ use this class to evaluate speed of model prediction """

    @task
    def predict(self):
        """ retrieve and verify prediction from ml-agent """
        expected = PAYLOAD['output']

        data = dict(example=PAYLOAD['example'])
        with self.client.post(PREDICT_URL, data=json.dumps(data), catch_response=True, headers=HEADERS) as response:
            if not precision_compare(expected, json.loads(response.content)['prediction']):
                err = 'invalid response - expected: {exp}, actual: {act}'.format(exp=expected, act=response.content)
                response.failure(err)


class WebsiteUser(HttpLocust):
    """ set up a locust tasked with building models """

    task_set = Predict
    min_wait = 2000
    max_wait = 5000
