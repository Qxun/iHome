# -*- coding: utf-8 -*-
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from Config import Config


db = SQLAlchemy()
redis_store = ''


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    # csrf验证
    CSRFProtect(app)
    # 设置session
    Session(app)
    return app