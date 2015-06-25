# -=- encoding: utf-8 -=-
from flask import request, abort

# from flask.ext.login import current_user
from flask.ext.restful import fields, marshal_with

from jeto import db
from jeto.core import clean
import requests as req
import json

from jeto.models.ssl import SSL
from jeto.models.domainController import DomainController
from jeto.services import RestrictedResource  # , adminAuthenticate
# from jeto.models.permission import ViewHostPermission
from jeto.services.domains import domain_controller_fields


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
            pass

    def put(self, id):
        """Update (override) an SSL cert/key"""
        pass
