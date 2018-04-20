# -*- coding: utf-8 -*-
from flask import request, jsonify, current_app

from iHome import redis_store, db
from iHome.models import User
from iHome.response_code import RET
from . import api

@api.route('/users', methods=['POST'])
def register():
    """
    注册功能实现
    1. 获取参数（手机号，短信验证码，密码），并校验
    2. redis读取短信验证码，
    3. 对比短信验证码
    4. 创建用户，并保存用户信息
    5. 添加信息到数据库
    6. 返回应答
    :return: 
    """
    # 1. 获取参数（手机号，短信验证码，密码），并校验
    req_dict = request.json
    mobile = req_dict.get('mobile')
    phonecode = req_dict.get('phonecode')
    password = req_dict.get('password')
    print req_dict

    if not all([mobile, phonecode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    # 2. redis读取短信验证码，
    try:
        sms_code = redis_store.get('sms_code:%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg='查询短信验证码失败')
    # 3. 对比短信验证码
    if sms_code != phonecode:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')

    # 4. 创建用户，并保存用户信息
    user = User()
    user.mobile = mobile
    user.name = mobile
    # 密码加密
    user.password_hash = password
    # 5. 添加信息到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errsmg='保存用户信息失败')
    # 6. 返回应答
    return jsonify(errno=RET.OK, errmsg='注册成功')
