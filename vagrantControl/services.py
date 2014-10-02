# -=- encoding: utf-8 -=-
import requests as req
from functools import wraps
from flask import request, json, abort
from flask.ext.restful import Resource, fields, marshal
# from flask.ext.restful import marshal_with
from flask.ext.login import current_user

from flask.ext.sqlalchemy import get_debug_queries

from vagrantControl import db
from vagrantControl import app
from vagrantControl.core import clean
from vagrantControl.models.vagrant import VagrantBackend
from vagrantControl.models.project import Project
from vagrantControl.models.host import Host
from vagrantControl.models.team import Team
from vagrantControl.models.user import User, ROLE_DEV, ROLE_ADMIN
from vagrantControl.models.permission import ViewHostPermission,\
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

project_fields = dict(
    project_wo_instance_fields,
    **{
        'instances': fields.Nested(instance_fields)
    }
)

domain_fields = {
    'slug': fields.String,
    'domain': fields.String,
    'ip': fields.String,
    'htpasswd': fields.String,
    'sslkey': fields.String,
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

        if 'state' in request.json and request.json['state'] == 'stop':
            if current_user.has_permission(StopInstancePermission, id):
                self.stop(id, machineName)
            else:
                abort(403)
        if 'state' in request.json and 'start' in request.json['state']:
            if current_user.has_permission(StartInstancePermission, id):
                self.start(id, machineName)
            else:
                abort(403)
        if 'state' in request.json and 'provision' in request.json['state']:
            if current_user.has_permission(ProvisionInstancePermission, id):
                self.provision(id, machineName)
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
    def get(self):
        r = req.get(self._get_url(), headers=self._get_headers())
        domains = r.json()['domains']

        return {
            'domains': map(lambda t: marshal(t, domain_fields), domains),
        }

    def post(self, slug=None):

        if 'slug' in request.json:
            # Should mean we are editing a domain
            slug = request.json['slug']
            content = self.put(slug)
        else:
            domain = request.json['domain']
            ip = request.json['ip']
            htpasswd = None
            sslkey = None
            if 'htpasswd' in request.json:
                htpasswd = request.json['htpasswd']
            if 'sslkey' in request.json:
                sslkey = request.json['sslkey']

            data = json.dumps({'site': domain, 'ip': ip, 'htpasswd': htpasswd,
                               'sslkey': sslkey})
            # Should mean we are adding a new domain
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
        htpasswd = None
        sslkey = None

        if 'htpasswd' in request.json and request.json['htpasswd'] is not None:
            htpasswd = request.json['htpasswd'].strip()
        if 'sslkey' in request.json and request.json['sslkey'] is not None:
            sslkey = request.json['sslkey'].strip()

        data = json.dumps({'site': domain, 'ip': ip, 'htpasswd': htpasswd,
                           'sslkey': sslkey})
        r = req.put(self._get_url() + '/{}'.format(slug),
                    headers=self._get_headers(),
                    data=data)

        return r.content

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
            return {'team': marshal(team, team_fields)}

    @adminAuthenticate
    def post(self, id=None):
        if 'state' in request.json and request.json['state'] == 'create':
            team = Team(
                None,
                request.json['name'],
            )
            db.session.add(team)
            db.session.commit()
        else:
            team = Team.query.get(id)
            # @TODO add update support

        return {
            'team': marshal(team, team_fields),
        }

    @adminAuthenticate
    def put(self, id):
        team = Team.query.get(id)
        usersId = request.json['users']
        users = []
        for userId in usersId:
            users.append(User.query.get(userId))

        team.users = users

        permissions = []
        for permission in request.json['permissionsGrid']:
            teamPermission = TeamPermissionsGrids()
            teamPermission.objectId = permission['objectId']
            teamPermission.action = permission['action']
            teamPermission.objectType = permission['objectType']
            permissions.append(teamPermission)

        team.permissions_grids = permissions

        db.session.add(team)
        db.session.commit()

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
