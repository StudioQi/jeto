from flask import render_template, send_file, Response, session
from vagrantControl import app, babel
from vagrantControl.core import api, redis_conn
from vagrantControl.services import InstanceApi, InstancesApi
from vagrantControl.services import DomainsApi
from vagrantControl.services import HtpasswordApi, HtpasswordListApi


@app.route('/')
@app.route('/instances')
@app.route('/instances/<id>')
@app.route('/domains')
@app.route('/domains/<id>')
@app.route('/htpassword')
@app.route('/htpassword/<slug>')
def basic_pages(**kwargs):
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_file('static/img/favicon.ico')


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
