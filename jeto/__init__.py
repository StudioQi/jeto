import logging
from logging import FileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_oauth import OAuth
from flask_login import LoginManager
from flask_principal import Principal
from .settings import LOGS

handler = FileHandler(LOGS)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

app = Flask(__name__)
app.config.from_object('jeto.settings')
app.url_map.strict_slashes = False
app.logger.addHandler(handler)

db = SQLAlchemy(app)
babel = Babel(app)
oauth = OAuth()

google = oauth.remote_app(
    'google',
    base_url='https://www.google.com/accounts/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    request_token_params={
        'scope': 'openid profile email',
        'response_type': 'code'
    },
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    consumer_key=app.config['GOOGLE_CLIENT_ID'],
    consumer_secret=app.config['GOOGLE_CLIENT_SECRET']
)

principal = Principal(app)
lm = LoginManager(app)

import jeto.core
import jeto.controllers, jeto.controllers.login
from jeto.models.team import Team
from jeto.models.vagrant import VagrantInstance
from jeto.models.permission import TeamPermissionsGrids, UserPermissionsGrids
from jeto.models import *
from jeto.services import *
