# -*- coding: utf-8 -*-
# pylint: disable=relative-import
"""
Script to run gevent wsgi server
"""

from gevent.wsgi import WSGIServer
import argparse
from predict.app_factory import create_app
from predict.configurations import config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=8080, type=int, help='Server port')
    parser.add_argument('--env', default='test', choices=config.keys(), help='Configuration Environment')
    pargs = parser.parse_args()

    wgsi = create_app(env=pargs.env)

    http_server = WSGIServer(listener=('', pargs.port), application=wgsi)
    http_server.serve_forever()
