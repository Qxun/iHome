# -*- coding: utf-8 -*-
from flask import request, abort, jsonify, make_response

from iHome import redis_store, constants
from iHome.response_code import RET
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
    uuid = request.args.get('cur_id')
    if not uuid:
        abort(403)
    # 2.生成图片验证码
    name, text, data = captcha.generate_captcha()
    # 3.在redis中存储图片验证码
    try:
        redis_store.set('imagecode:%s' %uuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        print e
        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')
    # 4.返回图片验证码
    response = make_response(data)
    response.headers['Content-Type'] = 'image/jpg'
    return response
