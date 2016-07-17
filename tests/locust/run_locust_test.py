# -*- coding: utf-8 -*-
""" wrapper for locust testing """

import argparse
import json
import requests
from subprocess import Popen
from tests.predict.conftest import get_vw_payload
import time


MODEL_ID = 1
BUILD_URL = '/v1/models/{}'.format(MODEL_ID)
HEADERS = {'Content-type': 'application/json'}
HOST = 'http://localhost'
SLEEP = 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('locustfile', type=str, help='Path for locustfile to run')
    parser.add_argument('-p', '--port', dest='port', default='8080', type=int,
                        help='Port to use for ml-agent (default=8080)')
    pargs = parser.parse_args()

    ml_agent = None
    locust = None

    try:
        # start service
        ml_agent = Popen('python run_server.py --port {} --env test'.format(pargs.port), shell=True)
        time.sleep(SLEEP)

        host = '{host}:{port}'.format(host=HOST, port=pargs.port)

        # setup model
        response = requests.put(url='{host}{url}'.format(host=host, url=BUILD_URL),
                                data=json.dumps(get_vw_payload(1)),
                                headers=HEADERS)
        assert response.status_code == 200

        # run locust tests
        locust = Popen('locust -f {file} --host={host}'.format(file=pargs.locustfile, host=host), shell=True)
        time.sleep(SLEEP)
        # start page in a single process so closing it concludes test
        browser = Popen('open http://localhost:8089', shell=True)
        time.sleep(SLEEP)

        print "Press ctrl-c to stop test..."

        while browser.poll() is not None:
            time.sleep(SLEEP)

    finally:
        # stop service
        if locust is not None:
            locust.terminate()

        if ml_agent is not None:
            ml_agent.terminate()
