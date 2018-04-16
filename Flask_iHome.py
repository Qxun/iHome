# -*- coding: utf-8 -*-
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect


class Config(object):
    DEBUG = True

    SECRET_KEY = 'rrpDy8f5fTTRKjS9ffEeZ/DtOygD2e6b+nTGgNXya1aZVA2C47XuPIgFz8WhCu6M'
    # 配置mysql数据库连接
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/ihome'
    # 关闭追踪数据库的修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 配置redis地址
    REDIS_HOST = '172.16.59.141'
    REDIS_PORT = 6379
    # session配置
    SESSION_TYPE = 'redis'
    # 设置session存储redis地址
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置session数据加密
    SESSION_USER_SIGNER = True
    # 设置session过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 2


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# csrf验证
CSRFProtect(app)
# 设置session
Session(app)


@app.route('/', methods=['POST', 'GET'])
def hello_world():
    # redis_store.set('age', 18)
    session['city'] = 'beijing'
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
