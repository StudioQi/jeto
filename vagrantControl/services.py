# -=- encoding: utf-8 -=-
import requests as req
from functools import wraps
from flask import request, json, abort
from flask.ext.restful import Resource, fields, marshal_with, marshal
from flask.ext.login import current_user

from vagrantControl import db
from vagrantControl.models.vagrant import VagrantBackend
from vagrantControl.models.project import Project
from vagrantControl.models.host import Host
from vagrantControl.models.team import Team
from vagrantControl.models.user import User

from settings import DOMAINS_API_URL, DOMAINS_API_PORT
from settings import HTPASSWORD_API_URL, HTPASSWORD_API_PORT
# from time import sleep

project_wo_instance_fields = {
    'id': fields.String,
    'name': fields.String,
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
}

instance_fields = {
    'id': fields.String,
    'name': fields.String,
    'path': fields.String,
    'status': fields.Nested(status_fields),
    'ip': fields.String,
    'environment': fields.String,
    'project': fields.Nested(project_wo_instance_fields),
    'host': fields.Nested(host_fields),
}

project_fields = {
    'id': fields.String,
    'name': fields.String,
    'instances': fields.Nested(instance_fields)
}

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

team_fields = {
    'id': fields.String,
    'name': fields.String,
    'users': fields.Nested(user_fields)
}


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

    @marshal_with(instance_fields)
    def get(self, id):
        instance = self._getInstance(id)
        instance.status = instance._status()
        instance.ip = instance._ip()
        return instance

    def post(self, id):
        instance = self._getInstance(id)

        changed = False
        if 'name' in request.json:
            if request.json['name'] != instance.name:
                instance.name = request.json['name']
                changed = True

        if changed:
            instance.save()

        if 'state' in request.json and request.json['state'] == 'stop':
            self.stop(id)
        if 'state' in request.json and 'start' in request.json['state']:
            provider = request.json['state'].replace('start-', '')
            self.start(id, provider)
        if 'state' in request.json and 'provision' in request.json['state']:
            self.provision(id)

    def provision(self, id):
        self.backend.provision(id)

    def stop(self, id):
        self.backend.stop(id)

    def start(self, id, provider):
        self.backend.start(id, provider)

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


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_admin():
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
            return {'project': marshal(project, project_fields)}

    def post(self, id=None):
        if 'state' in request.json and request.json['state'] == 'create':
            project = Project(None, request.json['name'])
            db.session.add(project)
            db.session.commit()
        else:
            project = Project.query.get(id)

        return {
            'project': marshal(project, project_fields),
        }

    def put(self, id):
        pass

    def delete(self, id):
        project = Project.query.get(id)
        db.session.delete(project)
        db.session.commit()


class HostApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            hosts = Host.query.order_by('name')
            return {
                'hosts': map(lambda t: marshal(t, host_fields), hosts),
            }
        else:
            host = Host.query.get(id)
            return {'host': marshal(host, host_fields)}

    def post(self, id=None):
        if 'state' in request.json and request.json['state'] == 'create':
            host = Host(
                None,
                request.json['name'],
                request.json['params'],
                request.json['provider']
            )
            db.session.add(host)
            db.session.commit()
        else:
            host = Host.query.get(id)
            # @TODO add update support

        return {
            'host': marshal(host, host_fields),
        }

    def put(self, id):
        pass

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

    def put(self, id):
        team = Team.query.get(id)
        usersId = request.json['users']
        users = []
        for userId in usersId:
            users.append(User.query.get(userId))

        team.users = users
        db.session.add(team)
        db.session.commit()

    def delete(self, id):
        team = Team.query.get(id)
        db.session.delete(team)
        db.session.commit()


class UserApi(RestrictedResource):
    def get(self, id=None):
        if id is None:
            users = User.query.order_by('name')
            return {
                'users': map(lambda t: marshal(t, user_fields), users),
            }
        else:
            user = User.query.get(id)
            return {'user': marshal(user, user_fields)}

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
            # @TODO add update support

        return {
            'user': marshal(user, user_fields),
        }

    def put(self, id):
        pass

    def delete(self, id):
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
