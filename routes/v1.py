import utils.aws_sign as aws_sign
import utils.hash_sign as acg_sign
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

def inital(order):
    # todo: verify data before process
    header = {"typ":"JWT","alg":"RS256"}
    payload = {
        "partner_id": "SR0001",
        "request_id": order['request_id'], # "6f81fafa-4d0e-4829-94d0-b349d58506b3"
        "terminal_id":"123test", # 
        "branch_id" :"123test", # 
        "trans_id": order['trans_id'], # 20180201TR000001
        "trans_datetime": order['ts'], # '2005-08-15T15:52:01+00:00'
        "description": order['desc'], # 'Lorem ipsum labore in.'
        "amount": order['amount'], # 26.5
        "redirect_uri": "%s/acg-cb/api/v1/update" % credit.callback_host
    }
    sheader = json.dumps(header).replace(": ", ":").replace(', ', ',')
    spayload = json.dumps(payload).replace(": ", ":").replace(', ', ',')
    data = '%s.%s' % (base64.urlsafe_b64encode(sheader.encode('utf-8')).decode("utf-8") , base64.urlsafe_b64encode(spayload.encode('utf-8')).decode("utf-8") )
    b64_signed = acg_sign.sign_data("config/key/SR-UAT-Sign-Key-20180807.pem", data)
    jwt = '%s.%s' % (data, b64_signed.decode("utf-8"))

    endpoint = 'https://testgateway.uat-activesg.com/merchant/transaction/initiate'
    path = '/merchant/transaction/initiate'
    body2 = 'version=v1&request=' + jwt
    host = 'testgateway.uat-activesg.com'
    headers = aws_sign.requestPrepare(endpoint, host, path, body2)
    r = requests.post(endpoint, data=body2, headers=headers)

    msg = json.loads(r.text)
    if 'data' in msg:
        msg_ary = msg['data'].split('.')
        res_payload = msg_ary[1]
        data = json.loads(base64.urlsafe_b64decode(res_payload + '=' * (-len(res_payload) % 4)).decode('utf-8'))
        for key in data:
            if key == 'qr_code':
                logger.info('got qrcode: %s' % data)
                return {"qrcode": data[key], "msg":"ok", "status_code": 11}
            if data['status_code'] == 'ERROR':
                logger.error('error when got qrcode: %s' % data)
                return {"qrcode": '', "msg":data['message'], "status_code": 1}
    else:
        logger.info('%s' % msg['message'])
        return {"msg": "not ok", "status_code": 0}
