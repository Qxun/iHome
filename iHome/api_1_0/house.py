# -*- coding: utf-8 -*-
from datetime import datetime

from iHome.utils.image_storage import image_storage
from . import api
from iHome.models import Area, House, Facility, HouseImage, Order
from iHome.response_code import RET
from flask import current_app, jsonify, request, g, session
from iHome import db, constants, redis_store
from iHome.utils.commons import login_required
import json


@api.route('/houses/index')
def get_house_index():
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(constants.HOME_PAGE_DATA_REDIS_EXPIRES).all()
    except Exception as e :
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取房屋信息失败')

    houses_dict_li = []
    for house in houses:
        houses_dict_li.append(house.to_basic_dict())

    return jsonify(errno=RET.OK, errmsg='OK', data=houses_dict_li)


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
    user_id = session.get('user_id', -1)

    return jsonify(errno=RET.OK, errmsg='OK', data={'house':house.to_full_dict(), 'user_id': user_id})


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


@api.route('/houses')
def get_house_list():
    area_id = request.args.get('aid')
    sort_key = request.args.get('sk', 'new')
    page = request.args.get('p')
    sd = request.args.get('sd')
    ed = request.args.get('ed')

    start_date = None
    end_date = None

    try:
        if area_id:
            area_id = int(area_id)
        page = int(page)
        if sd:
            start_date = datetime.strptime(sd, '%Y-%m-%d')
        if ed:
            end_date = datetime.strptime(ed, '%Y-%m-%d')
        if start_date and end_date:
            assert start_date < end_date, Exception('起始时间大于结束时间')

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')

    try:
        key = 'house:%s:%s:%s:%s' % (area_id, sd, ed, sort_key)
        res_json_str = redis_store.hget(key,page)
        if res_json_str:
            resp = json.loads(res_json_str)
            return jsonify(errno=RET.OK, errmsg='OK', data=resp)
    except Exception as e:
        current_app.logger.error(e)


    try:
        houses_query = House.query
        if area_id:
            houses_query = houses_query.filter(House.area_id==area_id)

        try:
            conflict_orders_li = []
            if start_date and end_date:
                conflict_orders_li = Order.query.filter(end_date>Order.begin_date, start_date<Order.end_date).all()
            elif start_date:
                conflict_orders_li = Order.query.filter(start_date<Order.end_date).all()
            elif end_date:
                conflict_orders_li = Order.query.filter(end_date>Order.begin_date).all()

            if conflict_orders_li:
                conflict_orders_id = [order.house_id for order in conflict_orders_li]
                houses_query = houses_query.filter(House.id.notin_(conflict_orders_id))
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='查询冲突订单失败')

        if sort_key == 'booking':
            houses_query = houses_query.order_by(House.order_count.desc())
        elif sort_key == 'price-inc':
            houses_query = houses_query.order_by(House.price)
        elif sort_key == 'price_des':
            houses_query = houses_query.order_by(House.price.desc())
        else:
            houses_query = houses_query.order_by(House.create_time.desc())

        #分页操作
        house_paginate = houses_query.paginate(page, constants.HOUSE_LIST_PAGE_CAPACITY, False)
        # 获取当前页的结果列表
        houses = house_paginate.items
        # 获取分页之后的总页数
        total_page = house_paginate.pages

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    houses_dict_li = []
    for house in houses:
        houses_dict_li.append(house.to_basic_dict())

    resp = {'houses':houses_dict_li, 'total_page': total_page}
    try:
        key = 'house:%s:%s:%s:%s' % (area_id, sd, ed, sort_key)
        pipeline = redis_store.pipeline()
        pipeline.multi()
        pipeline.hset(key, page, json.dumps(resp))
        pipeline.expire(key, constants.HOUSE_LIST_REDIS_EXPIRES)
        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg='OK', data=resp)


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
    try:
        areas_json_str = redis_store.get('areas')
        if areas_json_str:
            areas_dict_li = json.loads(areas_json_str)
            return jsonify(errno=RET.OK, errmsg='OK', data=areas_dict_li)
    except Exception as e:
        current_app.logger.error(e)

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

    try:
        redis_store.set('areas', json.dumps(areas_dict_list), constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg='OK', data=areas_dict_list)
