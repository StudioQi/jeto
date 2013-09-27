from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('vagrantControl.settings')
app.url_map.strict_slashes = False

db = SQLAlchemy(app)

import vagrantControl.core
import vagrantControl.models
import vagrantControl.controllers
