# -*- coding: utf-8 -*-
from flask import session, current_app, jsonify, request, g

from iHome import db, constants
from iHome.utils.commons import login_required
from iHome.models import User
from iHome.response_code import RET
from iHome.utils.image_storage import image_storage
from . import api


@api.route('/user/auth', methods=['POST'])
@login_required
def auth():
    # 获取用户信息并验证
    json_dict = request.json
    real_name = json_dict.get('real_name')
    id_card = json_dict.get('id_card')
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    #第三方验证
    # 设置用户实名认证信息
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.errno(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    if user.real_name and user.id_card:
        return jsonify(errno=RET.DATAERR,errmsg='已经实名认证')

    user.real_name = real_name
    user.id_card = id_card
    # 保存数据库
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据存储失败')

    return jsonify(errno=RET.OK, errmsg='实名认证成功')


@api.route('/user/name', methods=['PUT'])
@login_required
def set_user_name():
    """
    设置用户名
    1、接收用户名并进行校验
    2、设置用户用户名
    3、返回应答
    """
    # 1、接收用户名并进行校验
    req_dict = request.json
    username = req_dict.get('username')

    if not username:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    # 2、设置用户用户名
    user_id = g.user_id
    try:
        user = User.query.filter(User.name == username, User.id != user_id).first()
    except Exception as e:
        user = None
        current_app.logger.error(e)

    if user:
        return jsonify(errno=RET.DATAERR, errmsg='用户名已存在')

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    user.name = username

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='设置用户名失败')

    # 3、返回应答
    return jsonify(errno=RET.OK, errmsg='设置用户名成功')


@api.route('/user/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    """
    上传头像到七牛云
    1、获取上传图片文件
    2、上传图片到七牛云
    3、设置用户的头像记录
    4、返回应答
    :return: 
    """
    # 1、获取上传图片文件
    file = request.files.get('avatar')

    if not file:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    # 2、上传图片到七牛云
    try:
        key = image_storage(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传头像失败')

    # 3、设置用户的头像记录
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')

    user.avatar_url = key

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存头像记录失败')

    # 4、返回应答
    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='上传头像成功', data={'avatar_url': avatar_url})


@api.route('/user')
@login_required
def get_user_info():
    """
    获取个人信息
    0. 判断是否登录
    1. 获取当前登录用户id
    2. 根据用户id获取用户信息
    3. 返回应答
    :return: 
    """
    # 1. 获取当前登录用户id
    user_id = session.get('user_id')

    # 2. 根据用户id获取用户信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    # 3. 返回应答

    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict())
