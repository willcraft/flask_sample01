
import pprint
import jwt
import re

from flask import Flask, request as req, jsonify, json
from functools import wraps
from models import db, IntegrityError, User, Userlocation
from common import *

app = Flask(__name__)


# テーブル作成
def create_tables():
    db.connect()
    db.create_tables([User, Userlocation])


# DB接続
@app.before_request
def _db_connect():
    db.connect()


# DB切断
@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()


# Content-Typeのチェック
def check_content_type(content_type):
    def _check_content_type(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            app.logger.debug(req.headers)
            if not content_type in req.headers['Content-Type']:
                return jsonify(errors = ['request body of format is invalid']), Status.UNSUPPORTED_MEDIA_TYPE
            return func(*args, **kwargs)
        return decorated
    return _check_content_type


# JWT
def auth_jwt(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if req.headers.has_key('Authorization'):
            match_token = re.match(r"^Bearer (?P<token>.*)$", req.headers['Authorization'])
            if match_token is not None:
                token = match_token.group('token')
                try:
                    user_keys = jwt.decode(token, SECRET)
                    user = User.select().where(User.id == user_keys['userid'], User.mail == user_keys['mail']).first()
                    if user is None:
                        raise Excetion()
                except:
                    return jsonify(errors = ['Authentication error']), Status.UNAUTHORIZED

                return func(user, *args, **kwargs)

        return jsonify(errors = ['Authentication error']), Status.UNAUTHORIZED

    return decorated


# ユーザの追加、変更
@app.route('/users', methods = ['POST', 'PUT'])
@check_content_type('application/json')
def user_save():

    def save(user = None):

        is_new_user = user is None

        if is_new_user:
            user = User()

        req_json = req.json
        user.name = req_json.get('name', '')
        user.mail = req_json.get('mail', '')
        user.password = req_json.get('password', '')

        errors = user.validation()

        if not errors:
            user.save()
            token = jwt.encode({'userid': user.id, 'mail': user.mail}, SECRET)
            return jsonify(token = token.decode()), Status.CREATIVED if is_new_user else Status.SUCCESS
        else:
            return jsonify(errors = errors), Status.BAD_REQUEST

    if req.method == 'POST':
        return save()
    else:
        save_func = auth_jwt(save)
        return save_func()


# ユーザ削除
@app.route('/users', methods = ['DELETE'])
@check_content_type('application/json')
@auth_jwt
def user_delete(user):
    user.delete_instance()
    return '', Status.NO_CONTENT


# User get
@app.route('/users')
@app.route('/users/<userid>')
def users(userid = None):
    print(userid)
    user = jwt.decode(userid, SECRET)
    pprint.pprint(user)
    return "users!!!!"


# ログイン
@app.route('/login', methods = ['POST'])
@check_content_type('application/json')
def login():

    req_json = req.json

    mail = req_json.get('mail', '')
    password = req_json.get('password', '')

    if not mail or not password:
        return jsonify(errors = ['request parameter is incorrect']), Status.BAD_REQUEST

    user = User.select().where(User.mail == mail).first()

    if user is not None:
        if password == cipher.decrypt(user.password).decode():
            token = jwt.encode({'userid': user.id, 'mail': user.mail}, SECRET)
            return jsonify(token = token.decode()), Status.SUCCESS

    return jsonify(errors = ['request parameter is incorrect']), Status.BAD_REQUEST


# 位置情報登録
@app.route('/locations', methods = ['POST'])
@check_content_type('application/json')
@auth_jwt
def add_location(user):

    req_json = req.json

    location = Userlocation()
    location.user = user.id
    location.lat = req_json.get('lat', None)
    location.lng = req_json.get('lng', None)

    errors = location.validation()

    if not errors:
        location.save()
        return '', Status.SUCCESS
    else:
        return jsonify(errors = errors), Status.BAD_REQUEST




if __name__ == '__main__':
    app.run(port = 9000, debug = True)
