#!/usr/bin/python3
from flask import Flask, jsonify, abort, make_response, request
from bson.objectid import ObjectId
import json
import requests
import traceback
import datetime
from time import strftime
from pytz import timezone

import routes.v1 as v1routes
# import utils.logger as logger

import logging
from logging.handlers import RotatingFileHandler
from flask.logging import default_handler

## API Server
app = Flask(__name__)

class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        record.utcnow = datetime.datetime.now(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S %Z')
        record.path = request.path
        record.method = request.method
        record.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        return super().format(record)
formatter = RequestFormatter(
        "[%(utcnow)s] [%(levelname)s] [%(remote_addr)s] [%(method)s @ %(path)s] [%(module)s@%(lineno)d] %(message)s"
    )
strm = logging.StreamHandler()
strm.setLevel(logging.DEBUG)
strm.setFormatter(formatter)

app.logger.removeHandler(default_handler)
app.logger.addHandler(strm)
app.logger.setLevel(logging.DEBUG)

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

@app.errorhandler(404)
def not_found(error):
    app.logger.info("not found")
    return make_response(jsonify({'msg': 'Not found'}), 404)

@app.after_request
def after_request(response):
    """ Logging after every request. """
    # This avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if not response.status_code < 400 and response.status_code != 404 and response.status_code < 500:
        app.logger.info("error: %s" % response.status)
    return response

@app.errorhandler(Exception)
def exceptions(e):
    """ Logging after every Exception. """
    ts = strftime('[%Y-%b-%d %H:%M]')
    tb = traceback.format_exc()
    app.logger.error('5xx INTERNAL SERVER ERROR\n %s' % tb)
    return "Internal Server Error", 500


# main routes
@app.route('/api/v1/version', methods=['GET'])
def get_version():
    app.logger.info("requested")
    return jsonify({"version": "v1"}), 200

@app.route('/api/v1/request', methods=['POST'])
def make_request():
    data_json = request.get_json(force=True, silent=True)
    if not data_json:
        app.logger.info("no json")
        return make_response(jsonify({'msg': 'No JSON'}), 404)
    app.logger.info("requested with: %s", data_json)
    response = v1routes.query(order)
    return jsonify(response), 200


if __name__ == '__main__':
    
    app.run(
    #    host='127.0.0.1', 
       host='0.0.0.0', 
       port=8899,
       debug=True
    )

