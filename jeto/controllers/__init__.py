from flask import render_template, send_file
from flask import g, abort, redirect, url_for
from flask.ext.login import current_user, login_required


from jeto import app, babel


@app.route('/')
def index(**kwargs):
    if current_user.is_anonymous:
        return redirect(url_for('login'), 307)
    else:
        return redirect(url_for('dashboard'), 307)


@app.route('/dashboard')
def dashboard():
    return render_template('index.j2')


@app.route('/instances')
@app.route('/instances/<id>')
@app.route('/domains')
@app.route('/domains/<id>')
@app.route('/htpassword')
@app.route('/htpassword/<slug>')
@app.route('/users/<id>/api-keys')
@login_required
def limited(**kwargs):
    return render_template('index.j2')


@app.route('/admin')
@app.route('/admin/<subType>')
@app.route('/admin/<subType>/<id>')
@login_required
def limited_admin(**kwargs):
    if not current_user.is_admin():
        return abort(403)

    return render_template('index.j2')


@app.route('/partials/<path:path>')
def partials(path):
    return render_template('partials/{}'.format(path))


@app.route('/favicon.ico')
def favicon():
    return send_file('static/img/favicon.ico')


@app.before_request
def before_request():
    g.user = current_user


@app.errorhandler(403)
def page_not_authorized(e):
    return render_template('403.j2'), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.j2'), 404


@babel.localeselector
def get_locale():
    return app.config['DEFAULT_LANGUAGE']

from jeto.core import api

from jeto.services.auditlog import AuditlogApi
from jeto.services.domains import DomainsApi, DomainControllerApi
from jeto.services.hosts import HostApi, HostsApi
from jeto.services.htpasswords import HtpasswordApi, HtpasswordListApi
from jeto.services.instances import InstanceApi, InstancesApi, CommandApi
from jeto.services.projects import ProjectApi
from jeto.services.ssl import SSLApi
from jeto.services.teams import TeamApi
from jeto.services.users import UserApi, CurrentUserApi
from jeto.services.api_keys import APIKeyApi

api.add_resource(InstanceApi, '/api/instance/<int:id>', endpoint='instance')
api.add_resource(InstancesApi, '/api/instances', endpoint='instances')
api.add_resource(InstanceApi, '/api/instance', endpoint='instance_creation')
api.add_resource(InstanceApi, '/api/instances/<int:id>/<machineName>/ip',
                 endpoint='machines')

api.add_resource(CommandApi, '/api/instances/<int:instance_id>/command',
                 endpoint='commands')
api.add_resource(CommandApi,
                 '/api/instances/<int:instance_id>/command/<command_id>',
                 endpoint='command_details')

api.add_resource(DomainsApi, '/api/domains', endpoint='domains')
api.add_resource(DomainsApi, '/api/domains/<int:id>')
api.add_resource(DomainControllerApi,
                 '/api/domainControllers',
                 endpoint='domainController')
api.add_resource(DomainControllerApi, '/api/domainControllers/<id>')

api.add_resource(HtpasswordApi, '/api/htpassword', endpoint='htpassword')
api.add_resource(HtpasswordListApi, '/api/htpassword/<slug>',
                 endpoint='htpasswordlist')

api.add_resource(ProjectApi, '/api/projects', endpoint='projects')
api.add_resource(ProjectApi, '/api/projects/<int:id>')

api.add_resource(HostsApi, '/api/hosts', endpoint='hosts')
api.add_resource(HostApi, '/api/host', endpoint='host')
api.add_resource(HostApi, '/api/host/<int:id>')

api.add_resource(TeamApi, '/api/teams', endpoint='teams')
api.add_resource(TeamApi, '/api/teams/<int:id>')

api.add_resource(UserApi, '/api/users', endpoint='users')
api.add_resource(UserApi, '/api/users/<id>')
api.add_resource(CurrentUserApi, '/api/users/current')

api.add_resource(AuditlogApi, '/api/auditlog', endpoint='Auditlog')
api.add_resource(AuditlogApi, '/api/auditlog/<int:id>')

api.add_resource(SSLApi, '/api/SSLKeys', endpoint='SSLKey')
api.add_resource(SSLApi, '/api/SSLKeys/<id>')

api.add_resource(APIKeyApi, '/api/APIKeys', endpoint='APIKeys')
api.add_resource(APIKeyApi, '/api/APIKeys/<userId>', endpoint='ApiKeysUser')
api.add_resource(APIKeyApi, '/api/APIKeys/<userId>/<int:id>')
