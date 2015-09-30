# -=- encoding: utf-8 -=-
import json
from flask import Response, request
from flask.ext.restful import fields, marshal
from jeto.models.auditlog import AuditLog
from flask.ext.login import current_user
from jeto.services import RestrictedResource  # , adminAuthenticate

auditlog_summary_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime(dt_format='iso8601'),
    'summary': fields.String
}

auditlog_details_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime(dt_format='iso8601'),
    'summary': fields.String,
    'objectId': fields.Integer,
    'objectType': fields.String,
    'objectName': fields.String,
    'request_details': fields.String,
    'user_id': fields.Integer,
    'user_name': fields.String,
}


class AuditlogApi(RestrictedResource):
    def get(self):
        PER_PAGE = 10
        data = request.args

        page = data.get('page', 1)
        limit = int(data.get('limit', PER_PAGE))
        offset = (int(page) - 1) * limit
        order_by = data.get('order_y', 'start_date')
        sorted = data.get('sorted', 'desc')
        if sorted.upper() not in ['ASC', 'DESC']:
            sorted = 'desc'

        logs = AuditLog.\
            query.\
            order_by('{} {}'.format(order_by, sorted)).\
            limit(limit).\
            offset(offset).\
            all()

        if current_user.is_admin():
            data = [marshal(log, auditlog_details_fields) for log in logs]
        else:
            data = [marshal(log, auditlog_summary_fields) for log in logs]

        response = Response(
            json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        response.headers['count'] = AuditLog.query.count()
        response.headers['per_page'] = PER_PAGE
        response.headers['page'] = page
        response.headers['limit'] = limit
        response.headers['offset'] = offset
        response.headers['order_by'] = order_by
        response.headers['sorted'] = sorted
        return response
