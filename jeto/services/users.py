
from flask import request

from flask_login import current_user
from flask_restful import fields, marshal
from flask_sqlalchemy import get_debug_queries

from jeto import db, app

from jeto.models.auditlog import auditlog
from jeto.models.user import User, ROLE_ADMIN, ROLE_DEV

from jeto.services import RestrictedResource, admin_authenticate
from jeto.services.teams import team_fields_wo_users


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


class CurrentUserApi(RestrictedResource):
    def get(self):
        return marshal(current_user, user_fields_with_teams)


class UserApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            users = User.query.order_by('name')
            return [marshal(user, user_fields_with_teams) for user in users]
        else:
            user = User.query.get(id)
            if user == current_user:
                user_fields_with_keys = dict(
                    user_fields,
                    **{
                        'api_keys': fields.Nested(api_key_fields)
                    }
                )
                return marshal(user, user_fields_with_keys)
            else:
                return marshal(user, user_fields_with_teams)

    @admin_authenticate
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

        return marshal(user, user_fields)

    @admin_authenticate
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
