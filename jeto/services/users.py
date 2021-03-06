
from flask import request

from flask.ext.restful import fields, marshal
from flask.ext.sqlalchemy import get_debug_queries
from flask_login import current_user
from jeto.models.auditlog import auditlog

from jeto import db, app

from jeto.services import RestrictedResource, adminAuthenticate
from jeto.services.teams import team_fields_wo_users

from jeto.models.user import User, ROLE_ADMIN, ROLE_DEV

api_key_fields = {
    'id': fields.Integer,
    'comment': fields.String,
    'name': fields.String,
}

user_fields = {
    'id': fields.String,
    'name': fields.String,
    'email': fields.String,
    'role': fields.String,
    'picture': fields.String,
}

user_fields_with_teams = dict(
    user_fields,
    **{
        'teams': fields.Nested(team_fields_wo_users)
    }
)


class UserApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            users = User.query.order_by('name')
            return {
                'users': map(lambda t: marshal(t, user_fields_with_teams),
                             users),
            }
        else:
            user = User.query.get(id)
            if user == current_user:
                user_fields_with_keys = dict(
                    user_fields,
                    **{
                        'api_keys': fields.Nested(api_key_fields)
                    }
                )
                return {'user': marshal(user, user_fields_with_keys)}
            else:
                return {'user': marshal(user, user_fields_with_teams)}

    @adminAuthenticate
    def post(self, id=None):
        if 'state' in request.json and request.json['state'] == 'create':
            user = User(
                None,
                request.json['name'],
            )
            auditlog(
                current_user,
                'create',
                user,
                request_details=request.json)
            db.session.add(user)
            db.session.commit()
        else:
            user = User.query.get(id)
            if 'user' in request.json and 'role' in request.json['user']:
                role = request.json['user']['role']
                if role == ROLE_ADMIN:
                    user.role = ROLE_ADMIN
                elif role == ROLE_DEV:
                    user.role = ROLE_DEV

            auditlog(
                current_user,
                'update',
                user,
                request_details=request.json)
            db.session.add(user)
            db.session.commit()

        return {
            'user': marshal(user, user_fields),
        }

    @adminAuthenticate
    def put(self, id):
        pass

    @adminAuthenticate
    def delete(self, id):
        user = User.query.get(id)
        auditlog(
            current_user,
            'delete',
            user)
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            app.logger.debug(get_debug_queries())
