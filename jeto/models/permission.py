#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from collections import namedtuple
from functools import partial
from flask_principal import Permission

from jeto import db

InstanceNeed = namedtuple('instance', ['method', 'value'])
StartInstanceNeed = partial(InstanceNeed, 'start')
StopInstanceNeed = partial(InstanceNeed, 'stop')
ProvisionInstanceNeed = partial(InstanceNeed, 'provision')
DestroyInstanceNeed = partial(InstanceNeed, 'destroy')
ViewInstanceNeed = partial(InstanceNeed, 'view')
RunScriptInstanceNeed = partial(InstanceNeed, 'runScript')
SyncInstanceNeed = partial(InstanceNeed, 'sync')
RSyncInstanceNeed = partial(InstanceNeed, 'rsync')

HostNeed = namedtuple('host', ['method', 'value'])
ViewHostNeed = partial(HostNeed, 'view')

ProjectNeed = namedtuple('project', ['method', 'value'])
ViewProjectNeed = partial(ProjectNeed, 'view')

DomainNeed = namedtuple('project', ['method', 'value'])
ViewDomainNeed = partial(DomainNeed, 'view')
CreateDomainNeed = partial(DomainNeed, 'create')
EditDomainNeed = partial(DomainNeed, 'edit')

SSLKeyNeed = namedtuple('sslkey', ['method', 'value'])
ViewSSLKeyNeed = partial(SSLKeyNeed, 'view')


class StartInstancePermission(Permission):
    def __init__(self, instance_id):
        need = StartInstanceNeed(unicode(instance_id))
        super(StartInstancePermission, self).__init__(need)


class StopInstancePermission(Permission):
    def __init__(self, instance_id):
        need = StopInstanceNeed(unicode(instance_id))
        super(StopInstancePermission, self).__init__(need)


class ProvisionInstancePermission(Permission):
    def __init__(self, instance_id):
        need = ProvisionInstanceNeed(unicode(instance_id))
        super(ProvisionInstancePermission, self).__init__(need)


class DestroyInstancePermission(Permission):
    def __init__(self, instance_id):
        need = DestroyInstanceNeed(unicode(instance_id))
        super(DestroyInstancePermission, self).__init__(need)


class ViewInstancePermission(Permission):
    def __init__(self, instance_id):
        need = ViewInstanceNeed(unicode(instance_id))
        super(ViewInstancePermission, self).__init__(need)


class RunScriptInstancePermission(Permission):
    def __init__(self, instance_id):
        need = RunScriptInstanceNeed(unicode(instance_id))
        super(RunScriptInstancePermission, self).__init__(need)


class SyncInstancePermission(Permission):
    def __init__(self, instance_id):
        need = SyncInstanceNeed(unicode(instance_id))
        super(SyncInstancePermission, self).__init__(need)


class RSyncInstancePermission(Permission):
    def __init__(self, instance_id):
        need = RSyncInstanceNeed(unicode(instance_id))
        super(RSyncInstancePermission, self).__init__(need)


class ViewHostPermission(Permission):
    def __init__(self, host_id):
        need = ViewHostNeed(unicode(host_id))
        super(ViewHostPermission, self).__init__(need)


class ViewProjectPermission(Permission):
    def __init__(self, project_id):
        need = ViewProjectNeed(unicode(project_id))
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
        need = ViewDomainNeed(unicode(project_id))
        super(ViewDomainPermission, self).__init__(need)


class EditDomainPermission(Permission):
    def __init__(self, project_id):
        need = EditDomainNeed(unicode(project_id))
        super(EditDomainPermission, self).__init__(need)


class CreateDomainPermission(Permission):
    def __init__(self, project_id):
        need = CreateDomainNeed(unicode(project_id))
        super(CreateDomainPermission, self).__init__(need)


class SSLKeyPermission(Permission):
    def __init__(self, ssl_id):
        need = ViewSSLKeyNeed(unicode(ssl_id))
        super(SSLKeyPermission, self).__init__(need)
