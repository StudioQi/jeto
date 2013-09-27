from flask import render_template, send_file
from vagrantControl import app
from vagrantControl.core import api
from vagrantControl.services import InstanceApi, InstancesApi


@app.route('/')
@app.route('/instances')
@app.route('/instances/<id>')
def basic_pages(**kwargs):
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_file('static/img/favicon.ico')


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
