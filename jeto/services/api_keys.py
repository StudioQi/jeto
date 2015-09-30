# -=- encoding: utf-8 -=-
from flask import request, abort

from flask_login import current_user
from flask_restful import fields, marshal_with

from jeto import db

from jeto.models.api import APIKey
from jeto.models.auditlog import auditlog
from jeto.services import RestrictedResource  # , adminAuthenticate
from jeto.services.users import user_fields
from uuid import uuid4

api_key_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'user': fields.Nested(user_fields),
}


class APIKeyApi(RestrictedResource):
    @marshal_with(api_key_fields)
    def get(self, userId=None, id=None):
        """Retrieve a list of API keys"""
        if id is not None:
            key = APIKey.query.get(id)
            if key.user == current_user or current_user.is_admin():
                return key
            else:
                abort(403)

        if userId == current_user.id or current_user.is_admin():
            marsh = APIKey.query.filter(APIKey.user_id == userId).all()
            return marsh
        else:
            abort(403)

    @marshal_with(api_key_fields)
    def post(self):
        query = request.args
        comment = query.get('comment')

        # @TODO : We should not bind the user to current_user, in case the
        # key was added by an admin to a user.
        user = current_user
        api_key = APIKey()

        # @TODO : We should make sure the name was not already provided, maybe
        # we are just changing the comment on this key.
        api_key.name = unicode(uuid4())
        api_key.user = user
        api_key.comment = comment or "Random API Key"
        auditlog(
            user,
            'create api key',
            api_key,
            request_details=request.get_json())
        db.session.add(api_key)
        db.session.commit()
        return api_key

    def delete(self, userId, id):
        """delete API Key"""
        key = APIKey.query.get(id)
        if key.user == current_user or current_user.is_admin():
            auditlog(current_user, 'delete api key', key)
            db.session.delete(key)
            db.session.commit()
        else:
            abort(403)
