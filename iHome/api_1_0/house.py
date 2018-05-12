# -*- coding: utf-8 -*-
from iHome.utils.image_storage import image_storage
from . import api
from iHome.models import Area, House, Facility, HouseImage
from iHome.response_code import RET
from flask import current_app, jsonify, request, g
from iHome import db, constants
from iHome.utils.commons import login_required

@api.route('/house/<int:house_id>')
def get_house_info(house_id):
    """
    获取房屋详细信息
    1. 根据房屋id 获取房屋信息
    2. 组织数据返回响应
    :param house_id: 
    :return: 
    # """
    # 1.根据房屋id 获取房屋信息
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库失败')

    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')
    # 2.组织数据返回响应
    return jsonify(errno=RET.OK, errmsg='OK', data=house.to_full_dict())


@api.route('/houses/image', methods=['POST'])
@login_required
def save_house_image():
    house_id = request.form.get('house_id')
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    file = request.files.get('house_image')

    if not file:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少图片')

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    try:
        key = image_storage(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传房屋图片失败')

    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = key

    if not house.index_image_url:
        house.index_image_url = key

    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        db.session.callback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋图片失败')

    image_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='OK', data={'img_url': image_url})


@api.route('/houses', methods=['POST'])
@login_required
def save_new_house():
    req_dict = request.json
    title = req_dict.get('title')
    price = req_dict.get('price')
    address = req_dict.get('address')
    area_id = req_dict.get('area_id')
    room_count = req_dict.get('room_count')
    acreage = req_dict.get('acreage')
    unit = req_dict.get('unit')
    capacity = req_dict.get('capacity')
    beds = req_dict.get('beds')
    deposit = req_dict.get('deposit')  # 房屋押金
    min_days = req_dict.get('min_days')
    max_days = req_dict.get('max_days')

    if not all(
            [title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    try:
        # 数据库中房屋的价格和押金以 分 保存
        price = float(price) * 100
        deposit = float(deposit) * 100
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    facility = req_dict.get('facility')

    try:
        facilitys = Facility.query.filter(Facility.id.in_(facility)).all()

        if facilitys:
            house.facilities = facilitys
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取房屋设施信息失败')

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋信息失败')

    return jsonify(errno=RET.OK, errmsg='ok', data={'house_id': house.id})


@api.route('/areas')
def get_area():
    """
    1.获取城区信息
    2.组织响应，返回数据
    :return: 
    """
    # 1.获取城区信息
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg='查询城区信息失败')
    # 2. 组织数据
    areas_dict_list = []
    for area in areas:
        areas_dict_list.append(area.to_dict())

    return jsonify(errno=RET.OK, errmsg='OK', data=areas_dict_list)
