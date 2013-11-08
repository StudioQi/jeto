from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel

app = Flask(__name__)
app.config.from_object('vagrantControl.settings')
app.url_map.strict_slashes = False

db = SQLAlchemy(app)
babel = Babel(app)

import vagrantControl.core
import vagrantControl.models
import vagrantControl.controllers
