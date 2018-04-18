# -*- coding: utf-8 -*-
import redis
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from Config import config_dict
from iHome.utils.commons import RegexConverter

db = SQLAlchemy()
redis_store = None


def create_app(config_name):
    app = Flask(__name__)

    config_cls = config_dict[config_name]
    app.config.from_object(config_cls)

    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=config_cls.REDIS_HOST, port=config_cls.REDIS_PORT)
    # csrf验证
    CSRFProtect(app)
    # 设置session
    Session(app)

    # 添加路由转换器
    app.url_map.converters['re'] = RegexConverter

    from iHome.api_1_0 import api
    app.register_blueprint(api, url_prefix='/api/v1.0')
    from iHome.web_html import html
    app.register_blueprint(html)

    return app
