import requests as req
from flask import request, json, abort

from flask_restful import Resource, fields, marshal
from flask_login import current_user

from jeto import db, app
from jeto.core import clean

from jeto.services import RestrictedResource, admin_authenticate
from jeto.models.domain import Domain, Upstream, Alias
from jeto.models.domainController import DomainController
from jeto.models.user import User
from jeto.models.auditlog import auditlog

from jeto.models.permission import ViewDomainPermission,\
    EditDomainPermission, CreateDomainPermission
from jeto.models.permission import TeamPermissionsGrids

domain_controller_fields = {
    'id': fields.String,
    'name': fields.String,
    'address': fields.String,
    'port': fields.String,
    'accept_self_signed': fields.Boolean,
}

aliases_fields = {
    'id': fields.Integer,
    'uri': fields.String,
}

upstream_fields = {
    'id': fields.Integer,
    'ip': fields.String,
    'port': fields.Integer,
    'port_ssl': fields.Integer,
    'websocket': fields.Boolean,
    'location': fields.String,
    'state': fields.String,
}

domain_fields = {
    'id': fields.Integer,
    'slug': fields.String,
    'uri': fields.String,
    'htpasswd': fields.String,
    'ssl_key': fields.String,
    'upstreams': fields.Nested(upstream_fields),
    'aliases': fields.Nested(aliases_fields),
    'domain_controller': fields.Nested(domain_controller_fields),
}

domain_controller_fields_with_domains = dict(
    domain_controller_fields,
    **{
        'domains': fields.Nested(domain_fields),
    }
)


class DomainsApi(Resource):
    def get(self, id=None):
        if id is None:
            domains = Domain.query.all()
            domains = filter(
                lambda domain: current_user.has_permission(
                    (
                        ViewDomainPermission,
                        EditDomainPermission,
                        CreateDomainPermission
                    ),
                    domain.domain_controller and
                    domain.domain_controller.id or None
                ),
                domains
            )
        else:
            domains = Domain.query.get(id)

        return marshal(domains, domain_fields)

    def post(self):
        # Should mean we are adding a new domain
        domain = self._edit_domain()
        app.logger.debug(
            (self._get_url(domain),
             self._get_headers(),
             json.dumps(marshal(domain, domain_fields)),
             self._get_verify(domain)))
        req.post(
            self._get_url(domain),
            headers=self._get_headers(),
            data=json.dumps(marshal(domain, domain_fields)),
            verify=self._get_verify(domain)
        )
        return self.get(domain.id)

    def _edit_domain(self, id=None):
        query = request.get_json()

        if id is None:
            domain = Domain()
            action = 'create'
        else:
            domain = Domain.query.get(id)
            action = 'update'
            for upstream in domain.upstreams:
                db.session.delete(upstream)

            for alias in domain.aliases:
                db.session.delete(alias)

            db.session.commit()
        uri = query['uri']
        htpasswd = query.get('htpasswd')
        ssl_key = query.get('ssl_key')
        aliases = query.get('aliases', [])
        domain_controller = query.get('domain_controller')

        domain.upstreams = []
        for upstreamInfo in query.get('upstreams', []):
            upstream = Upstream()
            upstream.ip = upstreamInfo['ip']
            upstream.port = upstreamInfo['port']
            upstream.websocket = upstreamInfo['websocket'] or False
            upstream.location = upstreamInfo['location'] or '/'
            upstream.port_ssl = upstreamInfo['port_ssl'] or None
            upstream.state = upstreamInfo['state']
            domain.upstreams.append(upstream)

        domain.aliases = []
        for aliasInfo in aliases:
            alias = Alias()
            alias.uri = aliasInfo['uri']
            domain.aliases.append(alias)

        domain.domain_controller = None
        if domain_controller:
            domain_controller = DomainController.query.get(
                domain_controller['id']
            )
            domain.domain_controller = domain_controller

        domain.uri = uri
        domain.htpasswd = htpasswd
        domain.ssl_key = ssl_key

        if id is None:
            if current_user.has_permission(
                CreateDomainPermission,
                getattr(domain.domain_controller, 'id')
            ) is False:
                return abort(403)
        else:
            if current_user.has_permission(
                EditDomainPermission,
                getattr(domain.domain_controller, 'id')
            ) is False:
                return abort(403)

        auditlog(
            current_user,
            '{} domain'.format(action),
            domain,
            request_details=request.get_json())

        db.session.add(domain)
        db.session.commit()
        return domain

    def delete(self, id):
        domain = Domain.query.get(id)
        auditlog(
            current_user,
            'delete domain',
            domain,
            request_details=request.get_json())
        url = self._get_url(domain) + '/{}'.format(id)
        verify = self._get_verify(domain)
        db.session.delete(domain)
        db.session.commit()
        req.delete(
            url=url,
            headers=self._get_headers(),
            verify=verify
        )
        return self.get()

    def _delete_on_dc(self, domain):
        url = self._get_url(domain) + '/{}'.format(domain.id)
        req.delete(
            url=url,
            headers=self._get_headers(),
            verify=self._get_verify(domain)
        )

    def put(self, id=None):
        domain = Domain.query.get(id)
        if current_user.has_permission(
            EditDomainPermission,
            getattr(domain.domain_controller, 'id')
        ):
            if 'domain_controller' in request.json:
                # If the controller is to be changed in the _edit,
                # Delete the domain on the current controller
                if domain.domain_controller is not None and\
                        request.json['domain_controller'] is not None:
                    self._delete_on_dc(domain)

                # If the domain is currently on the default controller and the
                # new controller is expected to be different, delete it on the
                # default controller
                if domain.domain_controller is None and\
                        request.json['domain_controller'] is not None:
                    self._delete_on_dc(domain)

                # If we are changing the controller to be the default one
                if domain.domain_controller is not None and\
                        request.json['domain_controller'] is None:
                    self._delete_on_dc(domain)

            domain = self._edit_domain(id)

            app.logger.debug(
                (
                    '{}/{}'.format(self._get_url(domain), id),
                    self._get_headers(),
                    json.dumps(marshal(domain, domain_fields)),
                    self._get_verify(domain)))
            req.put(
                '{}/{}'.format(self._get_url(domain), id),
                headers=self._get_headers(),
                data=json.dumps(marshal(domain, domain_fields)),
                verify=self._get_verify(domain)
            )

        return self.get(domain.id)

    def _get_url(self, domain=None):
        if domain is None or domain.domain_controller is None:
            return 'http://' + app.config.get('DOMAINS_API_URL') + ':' +\
                 app.config.get('DOMAINS_API_PORT')
        else:
            return domain.domain_controller.address + ':' +\
                domain.domain_controller.port

    def _get_headers(self):
        return {'Content-Type': 'application/json',
                'Accept': 'application/json'}

    def _get_verify(self, domain):
        if domain.domain_controller is not None:
            return domain.domain_controller.accept_self_signed

        return True


class DomainControllerApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            domain_controllers = DomainController.query.order_by('name')
            domain_controllers = filter(
                lambda domain_controller: current_user.has_permission(
                    (
                        ViewDomainPermission,
                        EditDomainPermission,
                        CreateDomainPermission
                    ),
                    domain_controller.id
                ),
                domain_controllers
            )
            return {
                'domain_controllers': map(
                    lambda t: marshal(
                        t,
                        domain_controller_fields_with_domains
                    ),
                    domain_controllers
                ),
            }
        else:
            domain_controller = DomainController.query.get(id)
            return marshal(
                domain_controller,
                domain_controller_fields_with_domains
            )

    @admin_authenticate
    def post(self):
        domain_controller = DomainController(
            None,
            request.json['name'],
            request.json['address'],
            request.json['port'],
            request.json['accept_self_signed']
        )
        auditlog(
            current_user,
            'create domaincontroller',
            domain_controller,
            request_details=request.get_json())
        db.session.add(domain_controller)
        db.session.commit()
        return self.get(domain_controller.id)

    @admin_authenticate
    def put(self, id):
        domain_controller = DomainController.query.get(id)
        name = clean(request.json['name'].rstrip())
        address = clean(request.json['address'].rstrip())
        port = clean(request.json['port'].rstrip())
        auditlog(
            current_user,
            'update domaincontroller',
            domain_controller,
            request_details=request.get_json())

        if name != '':
            domain_controller.name = name

        if address != '':
            domain_controller.address = address

        if port != '':
            domain_controller.port = port

        db.session.add(domain_controller)
        db.session.commit()
        return self.get(id)

    def _update_permissions(self, team):
        users = []
        if 'users' in request.json:
            usersId = request.json['users']
            for userId in usersId:
                users.append(User.query.get(userId))

        team.users = users

        permissions = []
        if 'permissionsGrid' in request.json:
            for permission in request.json['permissionsGrid']:
                team_permission = TeamPermissionsGrids()
                team_permission.objectId = permission['objectId']
                team_permission.action = permission['action']
                team_permission.objectType = permission['objectType']
                permissions.append(team_permission)

        team.permissions_grids = permissions

        return team

    @admin_authenticate
    def delete(self, id):
        domain_controller = DomainController.query.get(id)
        auditlog(
            current_user,
            'delete domaincontroller',
            domain_controller)
        db.session.delete(domain_controller)
        db.session.commit()
