# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, make_response, session

# 创建蓝图
from flask_wtf.csrf import generate_csrf

html = Blueprint('html', __name__)


# 蓝图注册路由
@html.route('/<re(".*"):file_name>')
# @html.route('/<file_name>')
def send_html_file(file_name):
    # 获取静态页面
    if file_name == '':
        file_name = 'index.html'

    if file_name != 'favicon.ico':
        file_name = 'html/' + file_name
    # file_name = 'html' + file_name
    response = make_response(current_app.send_static_file(file_name))
    csrf_token = generate_csrf()
    response.set_cookie('csrf_token', csrf_token)
    return response



