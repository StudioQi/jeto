from flask import request

from flask.ext.login import current_user
from flask.ext.restful import fields, marshal

from jeto import db
from jeto.core import clean

from jeto.models.host import Host
from jeto.models.auditlog import auditlog
from jeto.services import RestrictedResource, adminAuthenticate
from jeto.models.permission import ViewHostPermission


host_fields = {
    'id': fields.String,
    'name': fields.String,
    'provider': fields.String,
    'params': fields.String,
}


class HostApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            hostsAll = Host.query.order_by('name')
            permittedHosts = []
            for host in hostsAll:
                if current_user.has_permission(ViewHostPermission, host.id):
                    permittedHosts.append(host)

            return {
                'hosts': map(
                    lambda t: marshal(t, host_fields), permittedHosts
                ),
            }
        else:
            host = Host.query.get(id)
            host.params = host.params.replace('\r\n', '<br>')
            host.params = host.params.replace('\n', '<br>')

            return marshal(host, host_fields)

    @adminAuthenticate
    def post(self, id=None):
        if 'state' in request.json and request.json['state'] == 'create':
            host = Host(
                None,
                clean(request.json['name']),
                request.json['params'].replace("<br>", "\r\n"),
                clean(request.json['provider'])
            )
            auditlog(
                current_user,
                'create host',
                host)
            db.session.add(host)
            db.session.commit()
            return {
                'host': marshal(host, host_fields),
            }
        else:
            host = Host.query.get(id)
            auditlog(
                current_user,
                'update host',
                host)
            name = clean(request.json['name'].rstrip())

            params = request.json['params']
            while(params.find('<br><br>') != -1):
                params = params.replace("<br><br>", "<br>")

            params = params.replace("<br>", "\r\n")
            params = params.replace('<div>', '\r\n')
            params = params.replace('&nbsp;', '')
            params = params.replace('</div>', '\r\n')

            provider = clean(request.json['provider'].rstrip())

            if name != '':
                host.name = name
            if provider != '':
                host.provider = provider

            host.params = params

            db.session.add(host)
            db.session.commit()
            return self.get(id)

    @adminAuthenticate
    def put(self, id):
        pass

    @adminAuthenticate
    def delete(self, id):
        host = Host.query.get(id)
        auditlog(
            current_user,
            'delete host',
            host)
        db.session.delete(host)
        db.session.commit()
