DEBUG = True
SECRET_KEY = 'generate me'
aws_access_key_id = 'generate me'
aws_secret_access_key = 'generate me'

region = "us-east-1"
ami_default = "ami-49641c20"
size_default = "t1.micro"
keypair_name = "pierrepaul"
security_groups_default = "default group, need to be create beforehand for now"

try:
    from .settings.dev import *
except ImportError:
    pass

try:
    from .settings.pheromone import *
except ImportError:
    pass
