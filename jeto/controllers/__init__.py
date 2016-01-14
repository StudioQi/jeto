from flask import render_template, send_file
from flask import g, abort
from flask.ext.login import current_user, login_required


from jeto import app, babel


@app.route('/')
def index(**kwargs):
    return render_template('index.j2')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.j2')


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
def limitedAdmin(**kwargs):
    if not current_user.is_admin():
        return abort(403)

    return render_template('index.j2')


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
