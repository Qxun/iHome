# -*- coding: utf-8 -*-
from flask import request
from . import api
from iHome.utils.captcha.captcha import captcha


@api.route('/image_code')
def get_image_code():
    """
    生成图片验证码
    1.获取uuid
    2.生成图片验证码
    3.在redis中存储图片验证码
    4.返回图片验证码
    :return: 
    """
    # 1.获取uuid
    # 2.生成图片验证码
    name, text, data = captcha.generate_captcha()
    # 3.在redis中存储图片验证码
    # 4.返回图片验证码
    return data
