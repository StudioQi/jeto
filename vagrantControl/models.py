#-=- encoding: utf-8 -=-
#from time import sleep
#import vagrant
import gearman
import re
from vagrantControl import db
from vagrantControl import app
from flask.ext.sqlalchemy import orm
from flask import json
from flask import request
from sh import ls
from settings import ETH


class InvalidPath(Exception):
    pass


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

    def get(self, instanceId):
        return VagrantInstance.query.get(int(instanceId))

    def get_all_instances(self):
        return self.instances

    def create(self, request):
        if 'environment' in request:
            environment = request['environment']
        else:
            environment = ''

        instance = VagrantInstance(None, request['path'], request['name'],
                                   environment)
        if self._check_instance(request['path']):
            db.session.add(instance)
            db.session.commit()
        else:
            raise InvalidPath('Path {} given is invalid or cant be read'
                              .format(request['path']))

        return instance

    def delete(self, instanceId):
        instance = VagrantInstance.query.get(instanceId)
        db.session.delete(instance)
        db.session.commit()

    def _check_instance(self, path):
        try:
            ls(path + '/Vagrantfile')
        except:
            return False
        return True

    def stop(self, instanceId):
        instance = VagrantInstance.query.get(instanceId)
        return instance.stop()

    def start(self, instanceId, provider):
        instance = VagrantInstance.query.get(instanceId)
        return instance.start(provider)


class VagrantInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String)
    name = db.Column(db.String)
    environment = db.Column(db.String)

    def __init__(self, id, path, name, environment):
        self.id = id
        self.path = path
        self.name = name
        self.environment = environment
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
        #self.status = self._status()
        #if 'running' in self.status:
        #   self.ip = self._ip()

    def _status(self):
        args = {'path': self.path}
        results = json.loads(self._submit_job('status', args))
        results = re.findall(r'.*\n\n(.*)\n\n.*', results, re.M)
        #app.logger.debug(results)
        return results

    def _ip(self):
        args = {'path': self.path}
        results = self._submit_job('ip', args)
        return results

    def start(self, provider=None):
        args = {'path': self.path, 'eth': ETH, 'environment': self.environment}
        if provider:
            args['provider'] = provider

        #app.logger.debug(args)
        results = self._submit_job('start', args)
        self.status = self._status()
        return results

    def stop(self):
        args = {'path': self.path}
        results = self._submit_job('stop', args)
        self.status = self._status()
        return results

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def _submit_job(self, action, args):
        request = self.gm_client.submit_job(action,
                                            bytes(json.dumps(args)))
        return request.result
