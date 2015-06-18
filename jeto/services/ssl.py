# -=- encoding: utf-8 -=-
from flask import request

# from flask.ext.login import current_user
from flask.ext.restful import fields, marshal_with

from jeto import db, app
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
    """
    TODO:
      - model: link to domain controller
      - marshal: SSL
      - post:
        - get DC
        - if not exist: create in model
        - call nginx-api
    DONE:
    """
    def _get_verify(self, dc):
        if dc is not None:
            return dc.accept_self_signed

        return True

    @marshal_with(ssl_key_fields, envelope='keys')
    def get(self, dc=None):
        """Retrieve a list of SSL certs/keys"""
        # if dc:
            # return SSL.query.filter_by(domain_controller=dc)
        marsh = SSL.query.all()
        return marsh

    def post(self):
        """Send an SSL cert/key"""
        query = request.get_json()
        DC = clean(query.get('domain_controller'))
        name = clean(query.get('name'))
        value = clean(query.get('value'))
        new_cert = SSL()
        new_cert.name = name
        DC = DomainController.query.get(DC)
        new_cert.domain_controller = DC
        db.session.add(new_cert)
        db.session.commit()
        # if current_user.has_permission(ViewHostPermission, host.id):
        #     permittedHosts.append(host)
        app.logger.debug(dir(DC))
        req.post(
            DC.url + '/ssl',
            headers=json_headers,
            data=json.dumps(
                {'name': name,
                 'value': value}),
            verify=False
        )

    def delete(self, id):
        """delete SSL cert/key"""
        key = SSL.query.get(id)
        db.session.delete(key)
        req.delete(
            key.domain_controller.url + '/ssl/' + key.name,
            headers=json_headers,
            data=json.dumps(
                {'name': key.name}
            ),
        )

    def put(self, id):
        """Update (override) an SSL cert/key"""
        pass
