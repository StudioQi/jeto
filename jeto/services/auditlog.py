# -=- encoding: utf-8 -=-

from flask.ext.restful import fields, marshal
from jeto import db
from jeto.models.auditlog import AuditLog
from flask.ext.login import current_user
from jeto.services import RestrictedResource  # , adminAuthenticate


json_headers = {'Content-Type': 'application/json',
                'Accept': 'application/json'}

auditlog_summary_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime,
    'summary': fields.String
}

auditlog_details_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime,
    'summary': fields.String,
    'objectId': fields.Integer,
    'objectType': fields.String,
    'objectName': fields.String,
    'request_details': fields.String,
    'user_id': fields.Integer,
    'user_name': fields.String,
}


class AuditlogApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            return marshal(
                db.session.query(AuditLog).all() or {},
                auditlog_summary_fields)

        ret = (current_user.is_admin() and auditlog_details_fields or
               auditlog_summary_fields)
        return marshal(
            db.session.query(AuditLog).get(id) or {},
            ret)
