# -*- coding: utf-8 -*-
from flask import Blueprint

api = Blueprint('api_1_0', __name__)

# from index import hello_world
from verify import get_image_code