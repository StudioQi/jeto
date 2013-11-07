DEBUG = True
ETH = 'eth0'
SECRET_KEY = 'waiquohzi7OpealeiquahChaipautheiy1Giefah0thaw2ieD1Hae5eereimeix8quo5wimei8ohsh0lohweeng7moothah6aoshahcoo6'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/vagrantcontrol.db'
DOMAINS_API_IP = '127.0.0.1'
DOMAINS_API_PORT = '5000'

try:
    from .settings_dev import *
except ImportError:
    pass

try:
    from .settings_pheromone import *
except ImportError:
    pass
