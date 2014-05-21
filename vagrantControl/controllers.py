from flask import render_template, send_file, Response, session, url_for, redirect, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from requests import get, post
from vagrantControl import app, babel, google, lm, db
from vagrantControl.core import api, redis_conn
from vagrantControl.services import InstanceApi, InstancesApi
from vagrantControl.services import DomainsApi
from vagrantControl.services import HtpasswordApi, HtpasswordListApi
from vagrantControl.models import User
import json


@app.route('/')
@app.route('/instances')
@app.route('/instances/<id>')
@app.route('/domains')
@app.route('/domains/<id>')
@app.route('/htpassword')
@app.route('/htpassword/<slug>')
def index(**kwargs):
    return render_template('index.html')


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
    user = User.query.filter_by(id = int(data['id'])).first()
    if user is None:
        user = User(id = int(data['id']),
                    name = data['name'],
                    email = data['email'],
                    given_name = data['given_name'],
                    family_name = data['family_name'],
                    picture = data['picture'])
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
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/pubsub')
def pubsub():
    jobs = None
    output = ''
    if 'jobs' in session:
        jobs = session['jobs']
        for job in jobs:
            console = _read_console(job)
            output += console\
                .replace('\n', '<br />')\
                .replace('#BEGIN#', '')\
                .replace('#END#', '')
            if '#END#' in console:
                session['jobs'].remove(job)

    return Response('data: {}\n\n'.format(output),
                    mimetype='text/event-stream')


def _read_console(jobId):
    console = redis_conn.get('{}:console'.format(jobId))
    if console is None:
        console = ''
    return console


@app.route('/partials/<partial>')
@app.route('/partials/<typePartial>/<partial>')
def partials(partial, typePartial=None):
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
