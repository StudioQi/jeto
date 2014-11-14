# -=- encoding: utf-8 -=-

DEBUG = True
ETH = 'eth0'
SECRET_KEY = 'waiquohzi7OpealeiquahChaipautheiy1Giefah0thaw2ieD1Hae5eereimeix8\
quo5wimei8ohsh0lohweeng7moothah6aoshahcoo6'
SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/vagrantcontrol'
DOMAINS_API_URL = '127.0.0.1'
DOMAINS_API_PORT = '5000'
HTPASSWORD_API_URL = '127.0.0.1'
HTPASSWORD_API_PORT = '7000'
LANGUAGES = {
    'en': 'English',
    'fr': 'Français',
}
PROJECT_BASEPATH = '~/projects/'
# oauth
REDIRECT_URI = '/oauth2callback'
GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''
# GOOGLE_LIMIT_DOMAIN = ''
BRAND_IMAGE_EXTERNAL = None
BRAND_IMAGE_ASSET_FILENAME = None
DEFAULT_LANGUAGE = 'en'

try:
    from .settings_dev import *
except ImportError:
    pass

try:
    from .settings_pheromone import *
except ImportError:
    pass
