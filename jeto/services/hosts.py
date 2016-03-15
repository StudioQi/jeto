from flask import request

from flask_login import current_user
from flask_restful import fields, marshal

from jeto import db
from jeto.core import clean

from jeto.models.host import Host
from jeto.models.auditlog import auditlog
from jeto.services import RestrictedResource, admin_authenticate
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
            hosts_all = Host.query.order_by('name')
            permitted_hosts = []
            for host in hosts_all:
                if current_user.has_permission(ViewHostPermission, host.id):
                    permitted_hosts.append(host)

            return [marshal(host, host_fields) for host in permitted_hosts]
        else:
            host = Host.query.get(id)
            host.params = host.params.replace('\r\n', '<br>')
            host.params = host.params.replace('\n', '<br>')

            return marshal(host, host_fields)

    @admin_authenticate
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
                host,
                request_details=request.get_json())
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
                host,
                request_details=request.get_json())
            name = clean(request.json['name'].rstrip())

            params = request.json['params']
            while params.find('<br><br>') != -1:
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

    @admin_authenticate
    def delete(self, id):
        host = Host.query.get(id)
        auditlog(
            current_user,
            'delete host',
            host)
        db.session.delete(host)
        db.session.commit()
