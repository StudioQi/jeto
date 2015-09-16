# -=- encoding: utf-8 -=-
from flask import request

from flask.ext.login import current_user
from flask.ext.restful import fields, marshal_with

from jeto import db

from jeto.models.api import APIKeys
from jeto.services import RestrictedResource  # , adminAuthenticate
from jeto.services.users import user_fields
from uuid import uuid4


json_headers = {'Content-Type': 'application/json',
                'Accept': 'application/json'}

api_key_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'user': fields.Nested(user_fields),
}


class APIKeyApi(RestrictedResource):
    @marshal_with(api_key_fields, envelope='keys')
    def get(self, id=None):
        """Retrieve a list of API keys"""
        if id is not None:
            return APIKeys.query.get(id)
        marsh = APIKeys.query.all()
        return marsh

    def post(self):
        query = request.args
        comment = query.get('comment')
        user = current_user
        api_key = APIKeys()
        api_key.name = unicode(uuid4())
        api_key.user = user
        api_key.name = comment or "Random API Key"
        db.session.add(api_key)
        db.session.commit()

    def delete(self, id):
        """delete API Key"""
        key = APIKeys.query.get(id)
        db.session.delete(key)
        db.session.commit()
