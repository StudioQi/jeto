# -=- encoding: utf-8 -=-
from flask.ext.restful import Resource, fields, marshal_with, marshal
from flask import request, json
from vagrantControl.models import VagrantBackend
from settings import DOMAINS_API_URL, DOMAINS_API_PORT
from settings import HTPASSWORD_API_URL, HTPASSWORD_API_PORT
from vagrantControl import app
import requests as req
# from time import sleep


instance_fields = {
    'id': fields.String,
    'name': fields.String,
    'path': fields.String,
    'status': fields.List(fields.String),
    'ip': fields.String,
    'environment': fields.String,
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
            instance.start()
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
        # app.logger.debug(instance.ip)
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

        return self.get(id)

    def stop(self, id):
        self.backend.stop(id)
        return self.get(id)

    def start(self, id, provider):
        self.backend.start(id, provider)
        return self.get(id)

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
        app.logger.debug(r.json())
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
        app.logger.debug(data)
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
            print user
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
