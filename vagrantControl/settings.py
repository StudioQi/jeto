DEBUG = True
SECRET_KEY = 'waiquohzi7OpealeiquahChaipautheiy1Giefah0thaw2ieD1Hae5eereimeix8quo5wimei8ohsh0lohweeng7moothah6aoshahcoo6'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/vagrantcontrol.db'

size_default = "t1.micro"
keypair_name = "pierrepaul"

try:
    from .settings_dev import *
except ImportError:
    pass

try:
    from .settings_pheromone import *
except ImportError:
    pass
