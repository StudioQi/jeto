from flask import render_template, send_file, Response
from vagrantControl import app
from vagrantControl.core import api
from vagrantControl.services import InstanceApi, InstancesApi, DomainsApi


@app.route('/')
@app.route('/instances')
@app.route('/instances/<id>')
@app.route('/domains')
@app.route('/domains/<id>')
def basic_pages(**kwargs):
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_file('static/img/favicon.ico')


@app.route('/pubsub')
def pubsub():

    return Response('data: awdawd\n\n', mimetype='text/event-stream')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


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
