import logging
from logging import FileHandler

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel
from flask_oauth import OAuth
from flask.ext.login import LoginManager
from flask.ext.principal import Principal

handler = FileHandler('/var/log/vagrant-control/debug.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

app = Flask(__name__)
app.config.from_object('vagrantControl.settings')
app.url_map.strict_slashes = False
app.logger.addHandler(handler)

db = SQLAlchemy(app)
babel = Babel(app)
oauth = OAuth()
principal = Principal(app)

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'openid profile email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=app.config['GOOGLE_CLIENT_ID'],
                          consumer_secret=app.config['GOOGLE_CLIENT_SECRET'])

lm = LoginManager(app)

import vagrantControl.core
import vagrantControl.models.permission
import vagrantControl.models.vagrant
import vagrantControl.models.team
import vagrantControl.models.host
import vagrantControl.models.project
import vagrantControl.controllers
