# -=- encoding: utf-8 -=-
from functools import wraps
from flask import abort
from flask_login import current_user
from flask_restful import Resource
from flask_restful import fields

project_wo_instance_fields = {
    'id': fields.String,
    'name': fields.String,
    'git_address': fields.String,
    'base_path': fields.String,
}

team_permissions_grids_fields = {
    'id': fields.Integer,
    'objectId': fields.Integer,
    'objectType': fields.String,
    'action': fields.String,
}

team_fields_wo_users = {
    'id': fields.String,
    'name': fields.String,
    'permissions_grids': fields.Nested(team_permissions_grids_fields),
}


def admin_authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_admin():
            return func(*args, **kwargs)

        abort(403)
    return wrapper


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated():
            return func(*args, **kwargs)

        abort(403)
    return wrapper


class RestrictedResource(Resource):
    method_decorators = [authenticate]
