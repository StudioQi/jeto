# -=- encoding: utf-8 -=-

from flask.ext.restful import fields, marshal_with
from jeto import db
from jeto.models.auditlog import AuditLog
from jeto.services import RestrictedResource  # , adminAuthenticate


json_headers = {'Content-Type': 'application/json',
                'Accept': 'application/json'}

auditlog_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime,
    'summary': fields.String
}


class AuditlogApi(RestrictedResource):
    @marshal_with(auditlog_fields)
    def get(self):
        return db.session.query(AuditLog).all() or {}
