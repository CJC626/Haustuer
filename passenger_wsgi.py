import os
import jwt
import json
import hashlib
import configparser
import uuid
from database import dbutil
import time
import signal

from flask import Flask, request, render_template, redirect, url_for, Response, abort
from flask_cors import CORS

project_root = os.path.dirname(os.path.realpath('__file__'))
template_path = os.path.join(project_root, 'app/templates')
static_path = os.path.join(project_root, 'app/static')
config = configparser.ConfigParser()
config.read('config.ini')
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['global_config'] = config


@app.route('/auth', methods=['POST'])
def index():
    if request.method != 'POST':
        return "Invalid method: " + request.method
    username = request.json['username']
    password = request.json['password']
    dbconn = dbutil.connect_db(app.config['global_config'])
    userinfo = dbutil.get_user(username)
    valid_login = check_password(userinfo, password)
    if valid_login:
        resp = gen_jwt(userinfo)
    else:
        resp = {'error': 'Invalid Credentials'}
    return Response(json.dumps(resp), mimetype='application/json')


@app.route('/closedbconn', methods=['POST'])
def close_db_conn():
    if request.headers['Content-type'] != 'application/json':
        abort(415, 'Invalid Content-type: ' + request.content_type)
    print(request.data)
    dbutil.maybe_close_conn(app.config['global_config'], True)
    resp = {
        "success": True
    }
    return Response(json.dumps(resp), mimetype='application/json')


def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(user_info, user_password):
    if 'password' not in user_info.keys():
        return False
    password, salt = user_info['password'].split(":")
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


def gen_jwt(user_info):
    payload = {
        'username': user_info['username'],
        'firstname': user_info['firstname'],
        'lastname': user_info['lastname']
    }
    validtime = time.time()
    payload['startvalid'] = validtime
    payload['endvalid'] = validtime + 20 * 60
    secret = app.config['global_config']['SECURITY']['jwtsecret']
    jwtalg = app.config['global_config']['SECURITY']['jwtalg']
    encoded_jwt = jwt.encode(payload, secret, algorithm=jwtalg)
    return encoded_jwt


@app.teardown_appcontext
def teardown(error):
    dbutil.maybe_close_conn(app.config['global_config'], False)

