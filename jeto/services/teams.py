from flask import request

from flask_restful import fields, marshal, abort
from flask_login import current_user

from jeto import db, app
from jeto.core import clean
from jeto.services import RestrictedResource, admin_authenticate, team_fields_wo_users
from jeto.services.users import user_fields

from jeto.models.user import User
from jeto.models.team import Team
from jeto.models.permission import TeamPermissionsGrids
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
            return [marshal(team, team_fields) for team in teams]
        else:
            team = Team.query.get_or_404(id)
            return marshal(team, team_fields)

    @admin_authenticate
    def post(self):
        team = Team(
            None,
            request.json['name'],
        )
        auditlog(
            current_user,
            'create',
            team,
            request_details=request.json)
        db.session.add(team)
        db.session.commit()
        return self.get(team.id)

    @admin_authenticate
    def put(self, id):
        team = Team.query.get(id)
        name = clean(request.json['name'])
        if name != '':
            team.name = name
        team = self._update_permissions(team)
        auditlog(
            current_user,
            'update',
            team,
            request_details=request.json)
        db.session.add(team)
        db.session.commit()
        return self.get(team.id)

    def _update_permissions(self, team):
        users = []
        if 'users' in request.json:
            users_id = request.json['users']
            for user_id in users_id:
                users.append(User.query.get(user_id))

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
        team = Team.query.get(id)
        auditlog(
            current_user,
            'delete',
            team)
        db.session.delete(team)
        db.session.commit()
