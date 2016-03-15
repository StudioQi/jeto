import requests as req
from flask import request, json

from flask_restful import Resource, fields, marshal
from flask_login import current_user

from jeto import app
from jeto.models.auditlog import auditlog


htpassword_list_fields = {
    'slug': fields.String,
    'users': fields.List(fields.String),
}


class HtpasswordService(object):
    def _get_url(self):
        return 'http://' + app.config.get('HTPASSWORD_API_URL') + ':' +\
            app.config.get('HTPASSWORD_API_PORT')

    def _get_headers(self):
        return {
            "Content-Type": "application/json",
        }


class HtpasswordApi(Resource, HtpasswordService):
    def get(self):
        r = req.get(self._get_url())
        items = r.json()['lists']

        return [marshal(item, htpassword_list_fields) for item in items]

    def post(self, slug=None):
        name = request.json['name']

        data = json.dumps({'name': name})
        # Should mean we are adding a new user
        auditlog(
            current_user,
            'create',
            name, 'htpasswd',
            request_details=request.get_json())
        r = req.post(self._get_url(),
                     headers=self._get_headers(),
                     data=data)
        content = r.content

        return content

    def delete(self, slug):
        url = self._get_url() + '/{}'.format(slug)
        auditlog(
            current_user,
            'delete',
            slug, 'htpasswd')
        r = req.delete(url=url, headers=self._get_headers())
        return r.content

    def put(self, slug=None):
        domain = request.json['domain']
        ip = request.json['ip'].strip()
        data = json.dumps({'site': domain, 'ip': ip})
        auditlog(
            current_user,
            'update',
            slug,
            'htpasswd',
            request_details=request.get_json()
        )
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
        auditlog(
            current_user,
            'deleted',
            slug, 'htpasswd',
        )
        r = req.delete(self._get_url(slug))
        return r.content

    def put(self, slug):
        users = request.json['users']
        for user in users:
            if 'state' in user:
                if user['state'] == 'DELETE':
                    auditlog(
                        current_user,
                        'delete user {}'.format(
                            user['username']),
                        slug, 'htpasswd',
                        request_details=request.get_json())
                    req.delete(self._get_url(slug) +
                               '/{}'.format(user['username']))

                if user['state'] == 'CREATE':
                    auditlog(
                        current_user,
                        'add user {}'.format(user['username']),
                        slug, 'htpasswd',
                        request_details=request.get_json())
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
