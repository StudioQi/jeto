#-=- encoding: utf-8 -=-
from flask.ext.restful import Resource, fields, marshal_with, marshal
from flask import request
from vagrantControl.models import VagrantBackend
#from time import sleep


instance_fields = {
    'id': fields.String,
    'name': fields.String,
    'path': fields.String,
    'status': fields.String,
    'ip': fields.String,
    'environment': fields.String,
}


class InstancesApi(Resource):
    backend = None

    def __init__(self):
        self.backend = VagrantBackend()

    def get(self):
        instances = self.backend.get_all_instances()

        return {
            'instances': map(lambda t: marshal(t, instance_fields), instances),
        }

    def delete(self):
        instanceId = int(request.json['id'])
        self.backend.delete(instanceId)

    def post(self):
        if 'state' in request.json and request.json['state'] == 'start':
            instanceId = int(request.json['id'])
            instance = self.backend.get(instanceId)
            instance.start()
            return {
                'instance': marshal(instance, instance_fields),
            }

        if 'state' in request.json and request.json['state'] == 'stop':
            instanceId = int(request.json['id'])
            instance = self.backend.get(instanceId)
            instance.stop()
            return {
                'instance': marshal(instance, instance_fields),
            }

        if 'state' in request.json and request.json['state'] == 'create':
            instance = self.backend.create(request.json)
            return {
                'instance': marshal(instance, instance_fields),
            }

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

        if changed:
            instance.save()

        if 'state' in request and request.json['state'] == 'stop' and\
                instance.state != 'stopped':
            self.stop(id)
        if 'state' in request and request.json['state'] == 'start' and\
                instance.state != 'running':
            self.start(id)

        return self.get(id)

    def stop(self, id):
        self.backend.stop(id)
        return self.get(id)

    def start(self, id):
        self.backend.start(id)
        return self.get(id)

    def delete(self, id):
        instanceId = int(id)
        self.backend.delete(instanceId)

    def _getInstance(self, id):
        instances = self.backend.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance
