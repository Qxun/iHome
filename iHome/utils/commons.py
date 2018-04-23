# -*- coding: utf-8 -*-
import functools
from flask import session, g, jsonify
from werkzeug.routing import BaseConverter

from iHome.response_code import RET


class RegexConverter(BaseConverter):
    def __init__(self, url_map, regex):
        super(RegexConverter, self).__init__(url_map)

        self.regex = regex


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')

        if user_id:
            g.user_id = user_id
            return func(*args, **kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR, errmsg='用户未登录')
    return wrapper