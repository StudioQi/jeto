import logging, os
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel

basedir = os.path.abspath(os.path.dirname(__file__))
handler = RotatingFileHandler('{}/vc.log'.format(basedir), maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_object('vagrantControl.settings')
app.url_map.strict_slashes = False
app.logger.addHandler(handler)

db = SQLAlchemy(app)
babel = Babel(app)


import vagrantControl.core
import vagrantControl.models
import vagrantControl.controllers
