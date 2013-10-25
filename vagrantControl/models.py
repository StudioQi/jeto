#-=- encoding: utf-8 -=-
#from time import sleep
#import vagrant
import gearman
import json
from vagrantControl import db
from flask.ext.sqlalchemy import orm
from flask import request
from sh import ls
from settings import ETH


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

    def create(self, request):
        instance = VagrantInstance(None, request['path'], request['name'])
        if self._check_instance(request['path']):
            db.session.add(instance)
            db.session.commit()

        return instance

    def _check_instance(self, path):
        try:
            ls(path + '/Vagrantfile')
        except:
            return False
        return True


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
        self.ip = self._ip()

    def _status(self):
        args = {'path': self.path}
        results = self._submit_job('status', args)
        print results
        return results

    def _ip(self):
        args = {'path': self.path}
        results = self._submit_job('ip', args)
        return results

    def start(self):
        args = {'path': self.path, 'eth': ETH}
        results = self._submit_job('start', args)
        return results

    def stop(self):
        args = {'path': self.path}
        results = self._submit_job('stop', args)
        return results

    def _submit_job(self, action, args):
        request = self.gm_client.submit_job(action,
                                            bytes(json.dumps(args)))
        return request.result
