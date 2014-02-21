import logging
from logging import FileHandler

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel

handler = FileHandler('/var/log/vagrant-control/debug.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

app = Flask(__name__)
app.config.from_object('vagrantControl.settings')
app.url_map.strict_slashes = False
app.logger.addHandler(handler)

db = SQLAlchemy(app)
babel = Babel(app)


import vagrantControl.core
import vagrantControl.models
import vagrantControl.controllers
