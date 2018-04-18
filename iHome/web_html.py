# -*- coding: utf-8 -*-
from flask import Blueprint, current_app

# 创建蓝图
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
    return current_app.send_static_file(file_name)



