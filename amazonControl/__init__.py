from flask import Flask

app = Flask(__name__)

app.config.from_object('amazonControl.settings')

app.url_map.strict_slashes = False

import amazonControl.core
import amazonControl.models
import amazonControl.controllers
