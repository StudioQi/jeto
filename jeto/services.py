# -=- encoding: utf-8 -=-
import requests as req
from functools import wraps
from flask import request, json, abort
from flask.ext.restful import Resource, fields, marshal
# from flask.ext.restful import marshal_with
from flask.ext.login import current_user

from flask.ext.sqlalchemy import get_debug_queries

from jeto import db
from jeto import app
from jeto.core import clean
from jeto.models.vagrant import VagrantBackend
from jeto.models.project import Project
from jeto.models.host import Host
from jeto.models.team import Team
from jeto.models.domain import Domain, Upstream
from jeto.models.user import User, ROLE_DEV, ROLE_ADMIN
from jeto.models.permission import ViewHostPermission,\
    TeamPermissionsGrids, ProvisionInstancePermission,\
    StopInstancePermission, StartInstancePermission

from settings import DOMAINS_API_URL, DOMAINS_API_PORT
from settings import HTPASSWORD_API_URL, HTPASSWORD_API_PORT
# from time import sleep

project_wo_instance_fields = {
    'id': fields.String,
    'name': fields.String,
    'git_address': fields.String,
    'base_path': fields.String,
}

host_fields = {
    'id': fields.String,
    'name': fields.String,
    'provider': fields.String,
    'params': fields.String,
}

status_fields = {
    'name': fields.String,
    'status': fields.String,
    'ip': fields.String,
}

instance_fields = {
    'id': fields.String,
    'name': fields.String,
    'path': fields.String,
    'git_reference': fields.String,
    'status': fields.Nested(status_fields),
    'environment': fields.String,
    'project': fields.Nested(project_wo_instance_fields),
    'host': fields.Nested(host_fields),
}

upstream_fields = {
    'id': fields.Integer,
    'ip': fields.String,
    'port': fields.Integer,
    'port_ssl': fields.Integer,
    'state': fields.String,
}

domain_fields = {
    'id': fields.Integer,
    'slug': fields.String,
    'uri': fields.String,
    'htpasswd': fields.String,
    'ssl_key': fields.String,
    'upstreams': fields.Nested(upstream_fields),
}

htpassword_list_fields = {
    'slug': fields.String,
    'users': fields.List(fields.String),
}

user_fields = {
    'id': fields.String,
    'name': fields.String,
    'email': fields.String,
    'role': fields.String,
}

team_permissions_grids_fields = {
    'id': fields.Integer,
    'objectId': fields.Integer,
    'objectType': fields.String,
    'action': fields.String,
}

team_fields = {
    'id': fields.String,
    'name': fields.String,
    'users': fields.Nested(user_fields),
    'permissions_grids': fields.Nested(team_permissions_grids_fields),
}

team_fields_wo_users = {
    'id': fields.String,
    'name': fields.String,
    'permissions_grids': fields.Nested(team_permissions_grids_fields),
}

project_fields = dict(
    project_wo_instance_fields,
    **{
        'instances': fields.Nested(instance_fields),
        'teams': fields.Nested(team_fields)
    }
)

user_fields_with_teams = dict(
    user_fields,
    **{
        'teams': fields.Nested(team_fields_wo_users)
    }
)


class InstancesApi(Resource):
    backend = None

    def __init__(self):
        self.backend = VagrantBackend()

    def get(self):
        instances = self.backend.get_all_instances()

        return {
            'instances': map(lambda t: marshal(t, instance_fields), instances),
        }

    def delete(self):
        instanceId = int(request.json['id'])
        self.backend.delete(instanceId)

    def post(self):
        if 'state' in request.json and 'start' in request.json['state']:
            instanceId = int(request.json['id'])
            instance = self.backend.get(instanceId)
            provider = request.json['state'].replace('start-', '')
            instance.start(id, provider)
            return {
                'instance': marshal(instance, instance_fields),
            }

        if 'state' in request.json and request.json['state'] == 'stop':
            instanceId = int(request.json['id'])
            instance = self.backend.get(instanceId)
            instance.stop()
            return {
                'instance': marshal(instance, instance_fields),
            }

        if 'state' in request.json and request.json['state'] == 'create':
            instance = self.backend.create(request.json)
            return {
                'instance': marshal(instance, instance_fields),
            }

        return self.get()

    def _stop(self, id):
        self.backend.stop(id)

    def _start(self, id):
        self.backend.start(id)

    def _getInstance(self, id):
        instances = self.backend.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance


class InstanceApi(Resource):
    backend = None

    def __init__(self):
        self.backend = VagrantBackend()

    def get(self, id, machineName=None):
        instance = self._getInstance(id)

        if machineName is None:
            instance.status = instance._status()
        else:
            # app.logger.debug(instance._ip(machineName))
            return {'ip': instance._ip(machineName)}

        return marshal(instance, instance_fields)

    def post(self, id):
        instance = self._getInstance(id)

        changed = False
        if 'name' in request.json:
            if request.json['name'] != instance.name:
                instance.name = request.json['name']
                changed = True

        if changed:
            instance.save()

        if 'machine' in request.json:
            machineName = request.json['machine']

        states = {
            'stop': StopInstancePermission,
            'start': StartInstancePermission,
            'provision': ProvisionInstancePermission}
        state = request.json.get('state')
        permission = states.get(state)
        if permission:
            if current_user.has_permission(permission, id):
                getattr(self, state)(id, machineName)
            else:
                abort(403)

    def provision(self, id, machineName):
        self.backend.provision(id, machineName)

    def stop(self, id, machineName):
        self.backend.stop(id, machineName)

    def start(self, id, machineName):
        self.backend.start(id, machineName)

    def delete(self, id):
        instanceId = int(id)
        self.backend.delete(instanceId)

    def _getInstance(self, id):
        instances = self.backend.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance


class DomainsApi(Resource):
    def get(self, id=None):
        if id is None:
            domains = Domain.query.all()
        else:
            domains = Domain.query.get(id)

        return marshal(domains, domain_fields)

    def post(self, id=None):
        if id is None:
            domain = self._editDomain()
            # Should mean we are adding a new domain
            req.post(
                self._get_url(),
                headers=self._get_headers(),
                data=json.dumps(marshal(domain, domain_fields))
            )
            return self.get(domain.id)
        else:
            return self.put(id)

    def _editDomain(self, id=None):
        query = request.get_json()

        if id is None:
            domain = Domain()
        else:
            domain = Domain.query.get(id)

        uri = query['uri']
        htpasswd = query.get('htpasswd')
        ssl_key = query.get('ssl_key')
        state = query.get('state')

        domain.upstreams = []
        for upstreamInfo in query.get('upstreams', []):
            upstream = Upstream()
            upstream.ip = upstreamInfo['ip']
            upstream.port = upstreamInfo['port']
            upstream.port_ssl = upstreamInfo['port_ssl']
            upstream.state = upstreamInfo['state']
            domain.upstreams.append(upstream)

        domain.uri = uri
        domain.htpasswd = htpasswd
        domain.ssl_key = ssl_key

        db.session.add(domain)
        db.session.commit()
        return domain

    def delete(self, id):
        db.session.delete(Domain.query.get(id))
        db.session.commit()
        url = self._get_url() + '/{}'.format(id)
        req.delete(url=url, headers=self._get_headers())
        return self.get()

    def put(self, id=None):
        domain = self._editDomain(id)
        # Should mean we are adding a new domain
        req.put(
            '{}/{}'.format(self._get_url(), id),
            headers=self._get_headers(),
            data=json.dumps(marshal(domain, domain_fields))
        )

        return self.get(domain.id)

    def _get_url(self):
        return 'http://' + DOMAINS_API_URL + ':' + DOMAINS_API_PORT

    def _get_headers(self):
        return {'Content-Type': 'application/json',
                'Accept': 'application/json'}


class HtpasswordService(object):
    def _get_url(self):
        return 'http://' + HTPASSWORD_API_URL + ':' + HTPASSWORD_API_PORT

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
        }


class HtpasswordApi(Resource, HtpasswordService):
    def get(self):
        r = req.get(self._get_url())
        items = r.json()['lists']

        return {
            'lists': map(lambda t: marshal(t, htpassword_list_fields), items),
        }

    def post(self, slug=None):
        name = request.json['name']

        data = json.dumps({'name': name})
        # Should mean we are adding a new user
        r = req.post(self._get_url(),
                     headers=self._get_headers(),
                     data=data)
        content = r.content

        return content

    def delete(self, slug):
        url = self._get_url() + '/{}'.format(slug)
        r = req.delete(url=url, headers=self._get_headers())
        return r.content

    def put(self, slug=None):
        domain = request.json['domain']
        ip = request.json['ip'].strip()
        data = json.dumps({'site': domain, 'ip': ip})
        r = req.put(self._get_url() + '/{}'.format(slug),
                    headers=self._get_headers(),
                    data=data)

        return r.content


class HtpasswordListApi(Resource, HtpasswordService):
    def get(self, slug):
        r = req.get(self._get_url(slug))
        htpassword = r.json()
        return {'item': htpassword}

    def delete(self, slug):
        r = req.delete(self._get_url(slug))
        return r.content

    def put(self, slug):
        users = request.json['users']
        for user in users:
            if 'state' in user:
                if user['state'] == 'DELETE':
                    req.delete(self._get_url(slug) +
                               '/{}'.format(user['username']))

                if user['state'] == 'CREATE':
                    data = json.dumps({
                        'username': user['username'],
                        'password': user['password']
                    })
                    req.post(self._get_url(slug),
                             headers=self._get_headers(), data=data)

        return self.get(slug)

    def _get_url(self, slug):
        return super(HtpasswordListApi, self)._get_url() + '/{}'.format(slug)

    def _get_headers(self):
        return {'Accept': 'application/json',
                'Content-Type': 'application/json'}


def adminAuthenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_admin():
            return func(*args, **kwargs)

        abort(403)
    return wrapper


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated():
            return func(*args, **kwargs)

        abort(403)
    return wrapper


class RestrictedResource(Resource):
    method_decorators = [authenticate]


class ProjectApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            projects = Project.query.order_by('name')
            return {
                'projects': map(lambda t: marshal(t, project_fields), projects)
            }
        else:
            project = Project.query.get(id)
            project.teams = []
            teams = Team.query.all()
            for team in teams:
                if team.get_permissions_grids('project', project.id) is not\
                        None:
                    project.teams.append(team)

            return marshal(project, project_fields)

    @adminAuthenticate
    def post(self, id=None):
        if 'state' in request.json and request.json['state'] == 'create':
            project = Project(None, request.json['name'])
        else:
            project = Project.query.get(id)

        if 'name' in request.json\
                and request.json['name'] != '':
            project.name = request.json['name']
        if 'git_address' in request.json\
                and request.json['git_address'] != '':
            project.git_address = request.json['git_address']
        elif 'base_path' in request.json:
            project.base_path = request.json['base_path']

        db.session.add(project)
        db.session.commit()

        return marshal(project, project_fields)

    @adminAuthenticate
    def put(self, id):
        pass

    @adminAuthenticate
    def delete(self, id):
        project = Project.query.get(id)
        teams = Team.query.all()
        for team in teams:
            for permission in\
                    team.get_permissions_grids('project', project.id):
                db.session.delete(permission)

        db.session.delete(project)
        db.session.commit()


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
            app.logger.debug(host.params)
            db.session.add(host)
            db.session.commit()
            return {
                'host': marshal(host, host_fields),
            }
        else:
            host = Host.query.get(id)
            name = clean(request.json['name'].rstrip())
            params = request.json['params'].replace("<br>", "\r\n")
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
        db.session.delete(host)
        db.session.commit()


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
        db.session.delete(team)
        db.session.commit()


class UserApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            users = User.query.order_by('name')
            return {
                'users': map(lambda t: marshal(t, user_fields_with_teams),
                             users),
            }
        else:
            user = User.query.get(id)
            return {'user': marshal(user, user_fields_with_teams)}

    @adminAuthenticate
    def post(self, id=None):
        if 'state' in request.json and request.json['state'] == 'create':
            user = User(
                None,
                request.json['name'],
            )
            db.session.add(user)
            db.session.commit()
        else:
            user = User.query.get(id)
            if 'user' in request.json and 'role' in request.json['user']:
                role = request.json['user']['role']
                if role == ROLE_ADMIN:
                    user.role = ROLE_ADMIN
                elif role == ROLE_DEV:
                    user.role = ROLE_DEV

            db.session.add(user)
            db.session.commit()

        return {
            'user': marshal(user, user_fields),
        }

    @adminAuthenticate
    def put(self, id):
        pass

    @adminAuthenticate
    def delete(self, id):
        user = User.query.get(id)
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            app.logger.debug(get_debug_queries())
