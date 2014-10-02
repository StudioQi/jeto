from vagrantControl import app
from flask import request
from flask.ext.restful import Api
from redis import Redis
import re

api = Api(app)
redis_conn = Redis()


def is_async():
    if request.json and\
            'async' in request.json and\
            request.json['async'] is True:
        return True

    return False


def clean(string):
    return re.sub('<[^<]+?>', '', string)
