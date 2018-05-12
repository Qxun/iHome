# -*- coding: utf-8 -*-
from . import api
from iHome.models import Area, House, Facility
from iHome.response_code import RET
from flask import current_app, jsonify,request,g
from iHome import db
from iHome.utils.commons import login_required


@api.route('/houses', methods=['POST'])
@login_required
def save_new_house():
    print 123
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
    deposit = req_dict.get('deposit') # 房屋押金
    min_days = req_dict.get('min_days')
    max_days = req_dict.get('max_days')

    if not all([title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
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
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存房屋信息失败')

    return jsonify(errno=RET.OK, errmsg='ok')


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