#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from collections import namedtuple
from functools import partial
from flask.ext.principal import Permission

from vagrantControl import db

InstanceNeed = namedtuple('instance', ['method', 'value'])
StartInstanceNeed = partial(InstanceNeed, 'start')
StopInstanceNeed = partial(InstanceNeed, 'stop')
ProvisionInstanceNeed = partial(InstanceNeed, 'provision')
DestroyInstanceNeed = partial(InstanceNeed, 'destroy')
ViewInstanceNeed = partial(InstanceNeed, 'view')

HostNeed = namedtuple('instance', ['method', 'value'])
ViewHostNeed = partial(HostNeed, 'view')

ProjectNeed = namedtuple('project', ['method', 'value'])
ViewProjectNeed = partial(ProjectNeed, 'view')


class StartInstancePermission(Permission):
    def __init__(self, instanceId):
        need = StartInstanceNeed(unicode(instanceId))
        super(StartInstancePermission, self).__init__(need)


class StopInstancePermission(Permission):
    def __init__(self, instanceId):
        need = StopInstanceNeed(unicode(instanceId))
        super(StopInstancePermission, self).__init__(need)


class ProvisionInstancePermission(Permission):
    def __init__(self, instanceId):
        need = ProvisionInstanceNeed(unicode(instanceId))
        super(ProvisionInstancePermission, self).__init__(need)


class DestroyInstancePermission(Permission):
    def __init__(self, instanceId):
        need = DestroyInstanceNeed(unicode(instanceId))
        super(DestroyInstancePermission, self).__init__(need)


class ViewInstancePermission(Permission):
    def __init__(self, instanceId):
        need = ViewInstanceNeed(unicode(instanceId))
        super(ViewInstancePermission, self).__init__(need)


class ViewHostPermission(Permission):
    def __init__(self, instanceId):
        need = ViewInstanceNeed(unicode(instanceId))
        super(ViewHostPermission, self).__init__(need)


class ViewProjectPermission(Permission):
    def __init__(self, projectId):
        need = ViewProjectNeed(unicode(projectId))
        super(ViewProjectPermission, self).__init__(need)


class TeamPermissionsGrids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    objectId = db.Column(db.Integer)
    objectType = db.Column(db.String(64))
    action = db.Column(db.String(64))
    team_id = db.Column(
        db.Integer,
        db.ForeignKey('team.id')
    )


class UserPermissionsGrids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    objectId = db.Column(db.Integer)
    objectType = db.Column(db.String(64))
    action = db.Column(db.String(64))
    user_id = db.Column(
        db.String(64),
        db.ForeignKey('user.id')
    )
