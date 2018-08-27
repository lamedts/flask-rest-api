import json
import base64
import requests
import config.config as credit

from werkzeug.local import LocalProxy
from flask import current_app, jsonify
logger = LocalProxy(lambda: current_app.logger)

def query(order):
    logger.info('%s' % 'asdlfkj')
    return {"msg": "not ok", "status_code": 0}
