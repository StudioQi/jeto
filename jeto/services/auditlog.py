# -=- encoding: utf-8 -=-

from flask import Response
from flask.ext.restful import fields, marshal, request
import json

from jeto import db, app
from jeto.models.auditlog import AuditLog
from jeto.services import RestrictedResource

auditlog_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime,
    'summary': fields.String
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

        data = [marshal(log, auditlog_fields) for log in logs]
        app.logger.debug(json.dumps(data))
        response = Response(json.dumps(data), status=200, mimetype='application/json')
        response.headers['count'] = AuditLog.query.count()
        response.headers['per_page'] = PER_PAGE
        response.headers['page'] = page
        response.headers['limit'] = limit
        response.headers['offset'] = offset
        response.headers['order_by'] = order_by
        response.headers['sorted'] = sorted
        return response
