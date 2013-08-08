from flask import render_template, send_file
from amazonControl import app
from amazonControl.core import api
from amazonControl.services import InstanceApi, InstancesApi
from flask.ext.httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

users = {
    'montreal': 'python',
}


@auth.get_password
def get_pw(username):
    if username in users:
        return users[username]
    return None


@app.route('/')
@app.route('/instances')
@app.route('/instances/<id>')
@auth.login_required
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
    '/api/instances/<string:id>',
    endpoint='instance'
)

api.add_resource(
    InstancesApi,
    '/api/instances',
    endpoint='instances'
)
