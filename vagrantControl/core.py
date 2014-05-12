from vagrantControl import app
from flask.ext.restful import Api
from redis import Redis

api = Api(app)
redis_conn = Redis()
