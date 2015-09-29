from flask import request

from flask.ext.restful import fields, marshal
from jeto import db
from jeto.core import clean
from jeto.services import RestrictedResource, adminAuthenticate, team_fields_wo_users
from jeto.services.users import user_fields

from jeto.models.user import User
from jeto.models.team import Team
from jeto.models.permission import TeamPermissionsGrids
from flask.ext.login import current_user
from jeto.models.auditlog import auditlog

team_fields = dict(
    team_fields_wo_users,
    **{
        'users': fields.Nested(user_fields),
    }
)


class TeamApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            teams = Team.query.order_by('name')
            return {
                'teams': map(lambda t: marshal(t, team_fields), teams),
            }
        else:
            team = Team.query.get(id)
            return marshal(team, team_fields)

    @adminAuthenticate
    def post(self, id=None):
        if 'state' in request.json and request.json['state'] == 'create':
            team = Team(
                None,
                request.json['name'],
            )
            auditlog(
                current_user,
                'create',
                team)
            db.session.add(team)
            db.session.commit()
            return {
                'team': marshal(team, team_fields),
            }
        else:
            # Not used right now, put() is called instead.
            team = Team.query.get(id)
            name = clean(request.json['name'])
            if name != '':
                team.name = name

            # team = self._updatePermissions(team)

            db.session.add(team)
            db.session.commit()
            return self.get(id)

    @adminAuthenticate
    def put(self, id):
        team = Team.query.get(id)
        team = self._updatePermissions(team)
        auditlog(
            current_user,
            'update',
            team)
        db.session.add(team)
        db.session.commit()

    def _updatePermissions(self, team):
        users = []
        if 'users' in request.json:
            usersId = request.json['users']
            for userId in usersId:
                users.append(User.query.get(userId))

        team.users = users

        permissions = []
        if 'permissionsGrid' in request.json:
            for permission in request.json['permissionsGrid']:
                teamPermission = TeamPermissionsGrids()
                teamPermission.objectId = permission['objectId']
                teamPermission.action = permission['action']
                teamPermission.objectType = permission['objectType']
                permissions.append(teamPermission)

        team.permissions_grids = permissions

        return team

    @adminAuthenticate
    def delete(self, id):
        team = Team.query.get(id)
        auditlog(
            current_user,
            'delete',
            team)
        db.session.delete(team)
        db.session.commit()
