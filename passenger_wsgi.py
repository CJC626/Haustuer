import os
import jwt
import json
import hashlib
import configparser
import uuid

from flask import Flask, request, render_template, redirect, url_for, Response
from flask_cors import CORS

project_root = os.path.dirname(os.path.realpath('__file__'))
template_path = os.path.join(project_root, 'app/templates')
static_path = os.path.join(project_root, 'app/static')
config = configparser.ConfigParser()
config.read('config.ini')
app = Flask(__name__, template_folder=template_path, static_folder=static_path)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/auth', methods=['POST'])
def index():
    if request.method != 'POST':
        return "Invalid method: " + request.method
    username = request.json['username']
    password = hash_password(request.json['password'])
    secret = config['SECURITY']['jwtsecret']
    jwtalg = config['SECURITY']['jwtalg']
    encoded_jwt = jwt.encode({'username': username, 'password': password}, secret, algorithm=jwtalg)
    decoded_jwt = jwt.decode(encoded_jwt, secret, algorithms=[jwtalg])
    resp = {'encodedJwt': encoded_jwt, 'decodedJwt': decoded_jwt}
    return Response(json.dumps(resp), mimetype='application/json')


def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(":")
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest


application = app
