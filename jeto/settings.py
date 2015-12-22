# -=- encoding: utf-8 -=-
import os

DEBUG = os.environ.get('DEBUG', '1') == '1'
LOGS = os.environ.get('LOGS', '/var/log/jeto/debug.log')
ETH = os.environ.get('ETH', 'eth0')
SECRET_KEY = os.environ.get('SECRET_KEY', 'waiquohzi7OpealeiquahChaipautheiy1Giefah0thaw2ieD1Hae5eereimeix8\
quo5wimei8ohsh0lohweeng7moothah6aoshahcoo6')
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'mysql://root:root@localhost/jeto')
DOMAINS_API_SCHEME = os.environ.get('DOMAINS_API_SCHEME', 'http')
DOMAINS_API_URL = os.environ.get('DOMAINS_API_URL', '127.0.0.1')
DOMAINS_API_PORT = os.environ.get('DOMAINS_API_PORT', '5000')
HTPASSWORD_API_SCHEME = os.environ.get('HTPASSWORD_API_SCHEME', 'http')
HTPASSWORD_API_URL = os.environ.get('HTPASSWORD_API_URL', '127.0.0.1')
HTPASSWORD_API_PORT = os.environ.get('HTPASSWORD_API_PORT', '7000')
LANGUAGES = os.environ.get('LANGUAGES', {
    'en': 'English',
    'fr': 'Français',
})
PROJECT_BASEPATH = os.environ.get(
    'PROJECT_BASEPATH',
    '/home/vagrant/projects/')
# oauth
REDIRECT_URI = os.environ.get('REDIRECT_URI', '/oauth2callback')
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
# GOOGLE_LIMIT_DOMAIN = os.environ.get('# GOOGLE_LIMIT_DOMAIN', ['test.com', 'example.com'])
BRAND_IMAGE_EXTERNAL = os.environ.get('BRAND_IMAGE_EXTERNAL', None)
BRAND_IMAGE_ASSET_FILENAME = os.environ.get('BRAND_IMAGE_ASSET_FILENAME', None)
DEFAULT_LANGUAGE = os.environ.get('DEFAULT_LANGUAGE', 'en')

try:
    from .settings_dev import *
except ImportError:
    pass

try:
    from .settings_pheromone import *
except ImportError:
    pass
