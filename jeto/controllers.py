from flask import render_template, send_file, Response, session, url_for
from flask import redirect, g, flash, abort, current_app, request
from flask import jsonify
from flask.ext.login import login_user, logout_user
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _
from flask.ext.restful import marshal

from flask.ext.principal import Identity, AnonymousIdentity
from flask.ext.principal import identity_changed, identity_loaded
from flask.ext.principal import UserNeed, RoleNeed
# from flask.ext.principal import Permission

from rq import Queue, Connection
import time
import json
import base64

from requests import get
import ansiconv

from jeto import app, babel, google, lm, db
from jeto.core import api, redis_conn
from jeto.services.instances import InstanceApi, InstancesApi
from jeto.services.domains import DomainsApi, DomainControllerApi
from jeto.services.htpasswords import HtpasswordApi, HtpasswordListApi
from jeto.services.projects import ProjectApi
from jeto.services.hosts import HostApi
from jeto.services.teams import TeamApi
from jeto.services.users import UserApi, user_fields
from jeto.services.ssl import SSLApi
from jeto.services.api_keys import APIKeyApi
from jeto.models.user import User
from jeto.models.api import APIKey
from jeto.models.project import Project
from jeto.models.permission import ViewHostPermission, ViewHostNeed
from jeto.models.permission import ProvisionInstanceNeed, DestroyInstanceNeed,\
    ViewInstanceNeed, StartInstanceNeed, StopInstanceNeed,\
    RunScriptInstanceNeed, SyncInstanceNeed
from jeto.models.permission import CreateDomainNeed, ViewDomainNeed,\
    EditDomainNeed


@app.route('/')
def index(**kwargs):
    return render_template('index.html', brand_image=get_brand_image())


@app.route('/instances')
@app.route('/instances/<id>')
@app.route('/domains')
@app.route('/domains/<id>')
@app.route('/htpassword')
@app.route('/htpassword/<slug>')
@app.route('/users/<id>/api-keys')
@login_required
def limited(**kwargs):
    return render_template('index.html', brand_image=get_brand_image())


@app.route('/admin')
@app.route('/admin/<subType>')
@app.route('/admin/<subType>/<id>')
@login_required
def limitedAdmin(**kwargs):
    if not current_user.is_admin():
        return abort(403)

    return render_template('index.html', brand_image=get_brand_image())


@app.route('/favicon.ico')
def favicon():
    return send_file('static/img/favicon.ico')


@app.route('/oauth2callback')
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token
    if access_token is None:
        return redirect(url_for('login'))

    headers = {'Authorization': 'OAuth {}'.format(access_token)}
    req = get('https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
    data = req.json()

    if 'GOOGLE_LIMIT_DOMAIN' in app.config and \
            app.config['GOOGLE_LIMIT_DOMAIN'] and \
            ('hd' not in data or
             data['hd'] not in app.config['GOOGLE_LIMIT_DOMAIN']):

        flash(
            _('Domain not allowed, please use an email associated with\
              the domain : {}').format(app.config['GOOGLE_LIMIT_DOMAIN'])
        )

        return redirect(url_for('index'))

    user = User.query.filter_by(id=int(data['id'])).first()
    if user:
        user.name = data['name']
        user.given_name = data['given_name']
        user.family_name = data['family_name']
        user.picture = data['picture']
    else:
        user = User(id=int(data['id']),
                    name=data['name'],
                    email=data['email'],
                    given_name=data['given_name'],
                    family_name=data['family_name'],
                    picture=data['picture'])

    identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for('index'))


@identity_changed.connect_via(app)
def on_identity_changed(sender, identity):
    identity_permissions(sender, identity)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity_permissions(sender, identity)


def identity_permissions(sender, identity):
    identity.user = current_user
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(unicode(current_user.id)))
        identity.provides.add(RoleNeed(unicode(current_user.role)))
        _set_permissions(current_user.get_permissions_grids(), identity)
        if current_user.teams:
            for team in current_user.teams:
                _set_permissions(team.get_permissions_grids(), identity)


def _set_permissions(permissions_grids, identity):
    if permissions_grids is not None:
        for permission in permissions_grids:
            if permission.objectType == 'host' and permission.action == 'view':
                _set_permissions_host(identity, permission)
            if permission.objectType == 'domainController':
                _set_permissions_domain_controller(identity, permission)
            if permission.objectType == 'project':
                project = Project.query.get(permission.objectId)
                for instance in project.instances:
                    viewPermission = ViewHostPermission(
                        unicode(instance.host.id)
                    )
                    if viewPermission.can():
                        _set_permissions_instance(
                            identity,
                            instance,
                            permission
                        )
                    else:
                        app.logger.debug(
                            'Not adding permission for instance {} in project {}, user {} has no\
                            access to host {}'
                            .format(
                                instance.name,
                                project.name,
                                current_user.email,
                                instance.host.id
                            )
                        )


def _set_permissions_host(identity, permission, host=None):
    objectId = permission.objectId
    if host:
        objectId = host.id
    if permission.action == 'view':
        identity.provides.add(ViewHostNeed(unicode(objectId)))


def _set_permissions_instance(identity, instance, permission):
    if permission.action == 'start':
        identity.provides.add(StartInstanceNeed(unicode(instance.id)))
    if permission.action == 'stop':
        identity.provides.add(StopInstanceNeed(unicode(instance.id)))
    if permission.action == 'provision':
        identity.provides.add(ProvisionInstanceNeed(unicode(instance.id)))
    if permission.action == 'destroy':
        identity.provides.add(DestroyInstanceNeed(unicode(instance.id)))
    if permission.action == 'view':
        identity.provides.add(ViewInstanceNeed(unicode(instance.id)))
    if permission.action == 'runScript':
        identity.provides.add(RunScriptInstanceNeed(unicode(instance.id)))
    if permission.action == 'sync':
        identity.provides.add(SyncInstanceNeed(unicode(instance.id)))


def _set_permissions_domain_controller(identity, permission):
    objectId = unicode(permission.objectId)
    if permission.action == 'create':
        identity.provides.add(CreateDomainNeed(objectId))
    if permission.action == 'edit':
        identity.provides.add(EditDomainNeed(objectId))
    if permission.action == 'view':
        identity.provides.add(ViewDomainNeed(objectId))


@app.route('/login')
def login():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route('/logout')
def logout():
    logout_user()
    session.pop('access_token')
    if 'jobs' in session:
        session.pop('jobs')

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    flash(_("I'll miss you..."))
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@lm.request_loader
def api_user(request):
    api_key = request.headers.get('X-JETO-KEY')
    if api_key:
        key = APIKey.query.filter_by(name=api_key).first()
        if key:
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(key.user.id))
            return key.user

    # finally, return None if both methods did not login the user
    return None


@lm.unauthorized_handler
def unauthorized_callback():
    flash(_('Please login to use this page'))
    return redirect(url_for('index'))


@app.route('/pubsub/<instanceId>')
def pubsub(instanceId=None):
    jobs = None
    output = ''
    # We keep all jobs for 10 hours
    redis_conn.zremrangebyscore(
        'jobs:{}'.format(instanceId),
        0,
        time.time() - 36000
    )

    if instanceId is not None:
        jobs = redis_conn.zrevrange(
            'jobs:{}'.format(instanceId), 0, 0, withscores=True
        )
        if jobs:
            for userId, job in jobs:
                    console = _read_console(job)
                    output += console\
                        .replace('\n', '<br />')\
                        .replace('#BEGIN#', '')\
                        .replace('#END#', '')
                    output = ansiconv.to_html(output)
                    # if '#END#' in console:
                    # Save job into the db auditlog

    return Response('data: {}\n\n'.format(output),
                    mimetype='text/event-stream')


def _read_console(jobId):
    console = redis_conn.get('{}:console'.format(jobId))
    if console is None:
        console = ''
    return console


@app.route('/api/jobdetails/<instanceId>')
def getJobAuthorOnLastJob(instanceId):
    jobs = redis_conn.zrevrange(
        'jobs:{}'.format(instanceId), 0, -1, withscores=True
    )
    details = {}
    if len(jobs) > 0:
        userId, timeStarted = jobs[0]

        timeStarted = time.ctime(float(timeStarted))
        user = User.query.get(userId)

        userInfos = []
        if user:
            userInfos = marshal(user, user_fields)

        details['user'] = userInfos
        details['time_started'] = timeStarted

    return jsonify(details)


@app.route('/partials/landing.html')
def partials():
    return render_template('partials/landing.html')


@app.route('/partials/<partial>')
@app.route('/partials/<typePartial>/<partial>')
@app.route('/partials/<typePartial>/<subType>/<partial>')
@login_required
def partialsLimited(partial, typePartial=None, subType=None):
    if typePartial is not None and typePartial == 'admin':
        if not current_user.is_admin():
            return render_template('partials/403.html'.format(partial))

        if subType is not None:
            return render_template(
                'partials/admin/{}/{}'.format(subType, partial)
            )

        return render_template('partials/admin/{}'.format(partial))

    elif typePartial:
        return render_template('partials/{}/{}'.format(typePartial, partial))
    else:
        return render_template('partials/{}'.format(partial))


@app.before_request
def before_request():
    g.user = current_user


@app.errorhandler(403)
def page_not_authorized(e):
    return render_template('403.html', brand_image=get_brand_image()), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', brand_image=get_brand_image()), 404


@babel.localeselector
def get_locale():
    return app.config['DEFAULT_LANGUAGE']


def get_brand_image():
    if 'BRAND_IMAGE_ASSET_FILENAME' in app.config and\
            app.config['BRAND_IMAGE_ASSET_FILENAME'] is not None:
        return url_for(
            'static',
            filename=app.config['BRAND_IMAGE_ASSET_FILENAME']
        )
    if 'BRAND_IMAGE_EXTERNAL' in app.config and\
            app.config['BRAND_IMAGE_EXTERNAL'] is not None:
        return app.config['BRAND_IMAGE_EXTERNAL']
    return None


@app.route('/api/projects/<int:projectId>/git-references')
def get_git_references(projectId):
    forceRefresh = bool(int(request.args.get('force')))
    project = Project.query.get(projectId)

    fullRefs = None
    if forceRefresh is False:
        fullRefs = redis_conn.get('project:{}:refs'.format(projectId))

    if fullRefs is None:
        with Connection():
            queue = Queue('low', connection=redis_conn)
            action = 'worker.get_git_references'

            job = queue.enqueue_call(
                func=action,
                timeout=900,
                args=(project.git_address, project.id)
            )
            while job.result is None:
                time.sleep(0.5)

            fullRefs = str(job.result)
            redis_conn.set('project:{}:refs'.format(projectId), fullRefs)

    return jsonify({'gitReferences': json.loads(fullRefs)})


api.add_resource(InstanceApi, '/api/instances/<int:id>', endpoint='instance')

api.add_resource(InstancesApi, '/api/instances', endpoint='instances')

api.add_resource(InstanceApi, '/api/instances/<int:id>/<machineName>/ip',
                 endpoint='machines')

api.add_resource(DomainsApi, '/api/domains', endpoint='domains')

api.add_resource(DomainsApi, '/api/domains/<int:id>')

api.add_resource(HtpasswordApi, '/api/htpassword', endpoint='htpassword')

api.add_resource(HtpasswordListApi, '/api/htpassword/<slug>',
                 endpoint='htpasswordlist')

api.add_resource(ProjectApi, '/api/projects', endpoint='projects')
api.add_resource(ProjectApi, '/api/projects/<int:id>')

api.add_resource(HostApi, '/api/hosts', endpoint='hosts')
api.add_resource(HostApi, '/api/hosts/<int:id>')

api.add_resource(TeamApi, '/api/teams', endpoint='teams')
api.add_resource(TeamApi, '/api/teams/<int:id>')

api.add_resource(UserApi, '/api/users', endpoint='users')
api.add_resource(UserApi, '/api/users/<id>')

api.add_resource(SSLApi, '/api/SSLKeys', endpoint='SSLKey')
api.add_resource(SSLApi, '/api/SSLKeys/<id>')

api.add_resource(APIKeyApi, '/api/APIKeys', endpoint='APIKeys')
api.add_resource(APIKeyApi, '/api/APIKeys/<userId>', endpoint='ApiKeysUser')
api.add_resource(APIKeyApi, '/api/APIKeys/<userId>/<int:id>')

api.add_resource(DomainControllerApi,
                 '/api/domainControllers',
                 endpoint='domainController')
api.add_resource(DomainControllerApi, '/api/domainControllers/<id>')
