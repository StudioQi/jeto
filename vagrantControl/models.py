#-=- encoding: utf-8 -=-
#from time import sleep
#import vagrant
import gearman
from vagrantControl import db
from flask.ext.sqlalchemy import orm
from flask import request


class BackendProvider():
    def stop(self, instanceId):
        raise NotImplementedError("Should have implemented this")

    def start(self, instanceId):
        raise NotImplementedError("Should have implemented this")

    def pause(self, instanceId):
        raise NotImplementedError("Should have implemented this")

    def kill(self, instanceId):
        raise NotImplementedError("Should have implemented this")

    def get_all_instances(self):
        raise NotImplementedError("Should have implemented this")


class VagrantBackend(BackendProvider):
    def __init__(self):
        self.instances = VagrantInstance.query.all()

    def get_all_instances(self):
        return self.instances


class VagrantInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String)
    name = db.Column(db.String)

    def __init__(self, id, path, name):
        self.id = id
        self.path = path
        self.name = name
        self.init_on_load()

    def __unicode__(self):
        return self.path

    def __str__(self):
        return self.__unicode__()

    def post(self):
        print request.json
        return self

    @orm.reconstructor
    def init_on_load(self):
        self.gm_client = gearman.GearmanClient(['localhost'])
        self.status = self._status()

    def _status(self):
        request = self.gm_client.submit_job('status', bytes(self.path))
        return request.result

    def start(self):
        request = self.gm_client.submit_job('start', bytes(self.path))
        print request.result

    def stop(self):
        request = self.gm_client.submit_job('stop', bytes(self.path))
        print request.result
