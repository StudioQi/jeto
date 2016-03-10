#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from collections import namedtuple
from functools import partial
from flask_principal import Permission

from jeto import db

instance_need = namedtuple('instance', ['method', 'value'])
start_instance_need = partial(instance_need, 'start')
stop_instance_need = partial(instance_need, 'stop')
provision_instance_need = partial(instance_need, 'provision')
destroy_instance_need = partial(instance_need, 'destroy')
view_instance_need = partial(instance_need, 'view')
run_script_instance_need = partial(instance_need, 'run_script')
sync_instance_need = partial(instance_need, 'sync')
rSync_instance_need = partial(instance_need, 'rsync')

host_need = namedtuple('host', ['method', 'value'])
view_host_need = partial(host_need, 'view')

project_need = namedtuple('project', ['method', 'value'])
view_project_need = partial(project_need, 'view')

domain_need = namedtuple('project', ['method', 'value'])
view_domain_need = partial(domain_need, 'view')
create_domain_need = partial(domain_need, 'create')
edit_domain_need = partial(domain_need, 'edit')

ssl_key_need = namedtuple('sslkey', ['method', 'value'])
view_ssl_key_need = partial(ssl_key_need, 'view')


class StartInstancePermission(Permission):
    def __init__(self, instance_id):
        need = start_instance_need(unicode(instance_id))
        super(StartInstancePermission, self).__init__(need)


class StopInstancePermission(Permission):
    def __init__(self, instance_id):
        need = stop_instance_need(unicode(instance_id))
        super(StopInstancePermission, self).__init__(need)


class ProvisionInstancePermission(Permission):
    def __init__(self, instance_id):
        need = provision_instance_need(unicode(instance_id))
        super(ProvisionInstancePermission, self).__init__(need)


class DestroyInstancePermission(Permission):
    def __init__(self, instance_id):
        need = destroy_instance_need(unicode(instance_id))
        super(DestroyInstancePermission, self).__init__(need)


class ViewInstancePermission(Permission):
    def __init__(self, instance_id):
        need = view_instance_need(unicode(instance_id))
        super(ViewInstancePermission, self).__init__(need)


class RunScriptInstancePermission(Permission):
    def __init__(self, instance_id):
        need = run_script_instance_need(unicode(instance_id))
        super(RunScriptInstancePermission, self).__init__(need)


class SyncInstancePermission(Permission):
    def __init__(self, instance_id):
        need = sync_instance_need(unicode(instance_id))
        super(SyncInstancePermission, self).__init__(need)


class RSyncInstancePermission(Permission):
    def __init__(self, instance_id):
        need = rSync_instance_need(unicode(instance_id))
        super(RSyncInstancePermission, self).__init__(need)


class ViewHostPermission(Permission):
    def __init__(self, host_id):
        need = view_host_need(unicode(host_id))
        super(ViewHostPermission, self).__init__(need)


class ViewProjectPermission(Permission):
    def __init__(self, project_id):
        need = view_project_need(unicode(project_id))
        super(ViewProjectPermission, self).__init__(need)


class TeamPermissionsGrids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(64))
    action = db.Column(db.String(64))
    team_id = db.Column(
        db.Integer,
        db.ForeignKey('team.id')
    )


class UserPermissionsGrids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(64))
    action = db.Column(db.String(64))
    user_id = db.Column(
        db.String(64),
        db.ForeignKey('user.id')
    )


class ViewDomainPermission(Permission):
    def __init__(self, project_id):
        need = view_domain_need(unicode(project_id))
        super(ViewDomainPermission, self).__init__(need)


class EditDomainPermission(Permission):
    def __init__(self, project_id):
        need = edit_domain_need(unicode(project_id))
        super(EditDomainPermission, self).__init__(need)


class CreateDomainPermission(Permission):
    def __init__(self, project_id):
        need = create_domain_need(unicode(project_id))
        super(CreateDomainPermission, self).__init__(need)


class SSLKeyPermission(Permission):
    def __init__(self, ssl_id):
        need = view_ssl_key_need(unicode(ssl_id))
        super(SSLKeyPermission, self).__init__(need)
