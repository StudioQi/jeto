from requests import get

from flask import current_app, session, render_template
from flask import url_for, flash, redirect
from flask_babel import gettext as _
from flask_login import login_user, logout_user, current_user

from flask_principal import Identity, AnonymousIdentity
from flask_principal import identity_changed, identity_loaded
from flask_principal import UserNeed, RoleNeed

from jeto import app, google, lm, db
from jeto.models.user import User
from jeto.models.api import APIKey
from jeto.models.project import Project
from jeto.models.permission import ViewHostPermission, ViewHostNeed
from jeto.models.permission import ProvisionInstanceNeed, DestroyInstanceNeed, \
    ViewInstanceNeed, StartInstanceNeed, StopInstanceNeed, \
    RunScriptInstanceNeed, SyncInstanceNeed
from jeto.models.permission import CreateDomainNeed, ViewDomainNeed, \
    EditDomainNeed


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
                    view_permission = ViewHostPermission(
                            unicode(instance.host.id)
                    )
                    if view_permission.can():
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
    object_id = permission.objectId
    if host:
        object_id = host.id
    if permission.action == 'view':
        identity.provides.add(ViewHostNeed(unicode(object_id)))


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
    return render_template('login.j2')


@app.route('/login/google')
def login_google():
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
