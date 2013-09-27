#-=- encoding: utf-8 -=-
from flask.ext.restful import Resource, fields, marshal_with, marshal
from flask import request
from vagrantControl.models import VagrantBackend


instance_fields = {
    'id': fields.String,
    'name': fields.String,
    'path': fields.String,
    'status': fields.String,
}


class InstancesApi(Resource):
    backend = None

    def get(self):
        self.backend = VagrantBackend()
        instances = self.backend.get_all_instances()
        running = 0
        stopped = 0

        return {
            'instances': map(lambda t: marshal(t, instance_fields), instances),
            'running': running,
            'stopped': stopped,
        }

    def delete(self):
        pass

    def post(self):
        pass
#        instances = request.json['instances']
#        for instance in instances:
#            instanceLive = self._getInstance(instance['id'])
#            if instanceLive.state != instance['state']:
#                if instance['state'] == 'stop':
#                    self._stop(instanceLive.id)
#                elif instance['state'] == 'start':
#                    self._start(instanceLive.id)

        return self.get()

    def _stop(self, id):
        self.backend.stop(id)

    def _start(self, id):
        self.backend.start(id)

    def _getInstance(self, id):
        instances = self.backend.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance


class InstanceApi(Resource):
    backend = None

    def __init__(self):
        self.backend = VagrantBackend()

    @marshal_with(instance_fields)
    def get(self, id):
        instance = self._getInstance(id)
        return instance

    def post(self, id):
        instance = self._getInstance(id)

        changed = False
        if request.json['name'] != instance.name:
            instance.name = request.json['name']
            changed = True

        if request.json['project'] != instance.project:
            instance.project = request.json['project']
            changed = True

        if request.json['test'] != instance.test:
            instance.test = request.json['test']
            changed = True

        if changed:
            instance.save()

        if request.json['state'] == 'stop' and instance.state != 'stopped':
            self.stop(id)
        if request.json['state'] == 'start' and instance.state != 'running':
            self.start(id)

        return self.get(id)

    def stop(self, id):
        self.backend.stop(id)
        return self.get(id)

    def start(self, id):
        self.backend.start(id)
        return self.get(id)

    def delete(self, id):
        pass

    def _getInstance(self, id):
        instances = self.backend.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance
