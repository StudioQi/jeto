from flask import render_template, send_file, Response, session, url_for
from flask import redirect, g, flash
from flask.ext.login import login_user, logout_user
from flask.ext.login import current_user, login_required
from flask.ext.babel import gettext as _
from requests import get
import ansiconv

from vagrantControl import app, babel, google, lm, db
from vagrantControl.core import api, redis_conn
from vagrantControl.services import InstanceApi, InstancesApi
from vagrantControl.services import DomainsApi
from vagrantControl.services import HtpasswordApi, HtpasswordListApi
from vagrantControl.models import User


@app.route('/')
def index(**kwargs):
    return render_template('index.html', brand_image=get_brand_image())


@app.route('/instances')
@app.route('/instances/<id>')
@app.route('/domains')
@app.route('/domains/<id>')
@app.route('/htpassword')
@app.route('/htpassword/<slug>')
@login_required
def limited(**kwargs):
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
            'hd' not in data or\
            data['hd'] != app.config['GOOGLE_LIMIT_DOMAIN']:

        flash(_('Domain not allowed, please use an email associated with\
              the domain : {}').format(app.config['GOOGLE_LIMIT_DOMAIN']))

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

    db.session.add(user)
    db.session.commit()

    login_user(user)
    return redirect(url_for('index'))


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
    flash(_("I'll miss you..."))
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@lm.unauthorized_handler
def unauthorized_callback():
    flash(_('Please login to use this page'))
    return redirect(url_for('index'))


@app.route('/pubsub/<instanceId>')
def pubsub(instanceId=None):
    jobs = None
    output = ''
    if 'jobs' in session:
        jobs = session['jobs']
        # session['jobs'] = []
        for job in jobs:
            app.logger.debug(job)
            if instanceId is not None and \
                    int(instanceId) == int(job['instanceId']):
                console = _read_console(job['jobId'])
                app.logger.debug(console)
                output += console\
                    .replace('\n', '<br />')\
                    .replace('#BEGIN#', '')\
                    .replace('#END#', '')
                output = ansiconv.to_html(output)
                if '#END#' in console:
                    session['jobs'].remove(job)

    return Response('data: {}\n\n'.format(output),
                    mimetype='text/event-stream')


def _read_console(jobId):
    console = redis_conn.get('{}:console'.format(jobId))
    if console is None:
        console = ''
    return console


@app.route('/partials/landing.html')
def partials():
    return render_template('partials/landing.html')


@app.route('/partials/<partial>')
@app.route('/partials/<typePartial>/<partial>')
@login_required
def partialsLimited(partial, typePartial=None):
    if typePartial:
        return render_template('partials/{}/{}'.format(typePartial, partial))
    else:
        return render_template('partials/{}'.format(partial))


@app.before_request
def before_request():
    g.user = current_user


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@babel.localeselector
def get_locale():
    return 'fr'


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


api.add_resource(
    InstanceApi,
    '/api/instances/<int:id>',
    endpoint='instance'
)

api.add_resource(
    InstancesApi,
    '/api/instances',
    endpoint='instances'
)

api.add_resource(
    DomainsApi,
    '/api/domains',
    endpoint='domains'
)

api.add_resource(DomainsApi, '/api/domains/<slug>')

api.add_resource(
    HtpasswordApi,
    '/api/htpassword',
    endpoint='htpassword'
)

api.add_resource(
    HtpasswordListApi,
    '/api/htpassword/<slug>',
    endpoint='htpasswordlist'
)
