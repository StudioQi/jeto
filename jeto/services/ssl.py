# -=- encoding: utf-8 -=-
import json
import requests as req

from flask import request, abort
from flask_login import current_user
from flask_restful import fields, marshal_with

from jeto import db
from jeto.core import clean

from jeto.models.ssl import SSL
from jeto.models.domainController import DomainController
from jeto.services import RestrictedResource
from jeto.services.domains import domain_controller_fields
from jeto.models.auditlog import auditlog


json_headers = {'Content-Type': 'application/json',
                'Accept': 'application/json'}

ssl_key_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'domain_controller': fields.Nested(domain_controller_fields),
}


class SSLApi(RestrictedResource):
    def _get_verify(self, dc):
        if dc is not None:
            return dc.accept_self_signed

        return True

    @marshal_with(ssl_key_fields, envelope='keys')
    def get(self, id=None):
        """Retrieve a list of SSL certs/keys"""
        query = request.args
        if id is not None:
            return SSL.query.get(id)
        if query is not None and 'domain_controller' in query:
            dc = clean(query.get('domain_controller'))
            return SSL.query.filter_by(domaincontroller_id=dc).all()
        marsh = SSL.query.all()
        return marsh

    def post(self):
        """Send an SSL cert/key"""
        query = request.get_json()
        DC = clean(query.get('domain_controller'))
        name = clean(query.get('name'))
        cert = clean(query.get('cert'))
        key = clean(query.get('key'))
        check = SSL.query.filter_by(
            domaincontroller_id=DC,
            name=name
            ).count()
        if check > 0:
            abort(400)
        new_cert = SSL()
        new_cert.name = name
        DC = DomainController.query.get(DC)
        new_cert.domain_controller = DC
        auditlog(
            current_user,
            'create',
            new_cert,
            request_details=request.get_json())
        db.session.add(new_cert)
        db.session.commit()
        req.post(
            DC.url + '/ssl',
            headers=json_headers,
            data=json.dumps(
                {'name': name,
                 'cert': cert,
                 'key': key}),
            verify=False
        )

    def delete(self, id):
        """delete SSL cert/key"""
        key = SSL.query.get(id)
        auditlog(
            current_user,
            'delete',
            key)
        db.session.delete(key)
        db.session.commit()
        try:
            req.delete(
                key.domain_controller.url + '/ssl/' + key.name,
                headers=json_headers,
                data=json.dumps(
                    {'name': key.name}
                ),
            )
        except:
            abort(500)
