from flask import request

from flask_restful import fields, marshal
from flask_login import current_user

from jeto import db
from jeto.core import clean
from jeto.services import RestrictedResource, admin_authenticate
from jeto.services import project_wo_instance_fields
from jeto.services.instances import instance_fields
from jeto.services.teams import team_fields
from jeto.models.project import Project
from jeto.models.team import Team
from jeto.models.auditlog import auditlog

project_fields = dict(
    project_wo_instance_fields,
    **{
        'instances': fields.Nested(instance_fields),
        'teams': fields.Nested(team_fields)
    }
)


class ProjectApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            projects = Project.query.order_by('name')
            return [marshal(project, project_fields) for project in projects]
        else:
            project = Project.query.get(id)
            project.teams = []
            teams = Team.query.all()
            for team in teams:
                if team.get_permissions_grids('project', project.id) is not\
                        None:
                    project.teams.append(team)

            return marshal(project, project_fields)

    @admin_authenticate
    def post(self, id=None):
        if 'state' in request.json and request.json['state'] == 'create':
            action = 'create'
            project = Project(None, request.json['name'])
        else:
            action = 'update'
            project = Project.query.get(id)

        if 'name' in request.json\
                and request.json['name'] != '':
            project.name = clean(request.json['name'])
        if 'git_address' in request.json\
                and request.json['git_address'] != '':
            project.git_address = clean(
                request.json['git_address'].replace(' ', '')
            )
        elif 'base_path' in request.json:
            project.base_path = request.json['base_path']

        auditlog(
            current_user,
            action,
            project,
            request_details=request.get_json())
        db.session.add(project)
        db.session.commit()

        return marshal(project, project_fields)

    @admin_authenticate
    def delete(self, id):
        project = Project.query.get(id)
        teams = Team.query.all()
        for team in teams:
            for permission in\
                    team.get_permissions_grids('project', project.id):
                db.session.delete(permission)
        auditlog(
            current_user,
            'delete',
            project)

        db.session.delete(project)
        db.session.commit()
