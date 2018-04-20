# -*- coding: utf-8 -*-
import random
import re
from string import lower

from flask import request, abort, jsonify, make_response, current_app
import json
from iHome import redis_store, constants
from iHome.models import User
from iHome.response_code import RET
from . import api
from iHome.utils.captcha.captcha import captcha
from iHome.utils.sms import CCP


@api.route('/sms_code', methods=['POST'])
def send_sms_code():
    """
    #发送短信验证码
    json
    1. 获取参数（手机号，验证码， uuid）
    2. 验证参数完整和校验
    3. 从redis中获取图片验证码，（取不到，验证码过期）
    4. 对比图片验证码
    5. 生成短信验证码
    6. 保存redis短信验证码，
    7. 发送短信验证码
    8. 返回信息，发送验证码成功
    """
    # 1. 获取参数（手机号，验证码， uuid）
    req_data = request.data
    req_dict = json.loads(req_data)
    mobile = req_dict.get('mobile')
    image_code = req_dict.get('image_code')
    image_code_id = req_dict.get('image_code_id')
    # 2. 验证参数完整和校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r"1[3456789]\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')

    if User.query.filter_by(name=mobile).all():
        return jsonify(errno=RET.PARAMERR, errmsg='用户已注册')

    # 3. 从redis中获取图片验证码，（取不到，验证码过期）
    try:
        real_image_id = redis_store.get('imagecode:%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询图片验证码错误')
    if not real_image_id:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')

    # 4. 对比图片验证码
    if lower(real_image_id) != lower(image_code):
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')

    # 5. 生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.info('短信验证码：' + sms_code)

    # 6. 保存redis短信验证码，
    try:
        redis_store.set('sms_code:%s' % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存验证码失败')

    # 7. 发送短信验证码
    res = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60],1)

    if res != 1:
        return jsonify(errno=RET.THIRDERR, errsmg='发送短信失败')

    # 8. 返回信息，发送验证码成功
    return jsonify(errno=RET.OK, errmsg='发送短信成功')


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
        redis_store.set('imagecode:%s' % uuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        current_app.logger.info('图片验证码:'+text)
    except Exception as e:
        # 生成日志并保存
        current_app.logger.error(e)

        return jsonify(errno=RET.DBERR, errmsg='保存图片验证码失败')
    # 4.返回图片验证码
    response = make_response(data)
    response.headers['Content-Type'] = 'image/jpg'
    return response
