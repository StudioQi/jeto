#-=- encoding: utf-8 -=-
from flask.ext.restful import Resource, fields, marshal_with, marshal
from flask import request
from amazonControl.models import Amazon


instance_fields = {
    'id': fields.String,
    'name': fields.String,
    'project': fields.String,
    'state': fields.String,
    'type': fields.String,
    'ip': fields.String,
    'public_dns': fields.String,
    'placement': fields.String,
    'test': fields.String,
}


class InstancesApi(Resource):
    def get(self):
        amazon = Amazon()
        instances = amazon.get_all_instances()
        running = 0
        regions = {}
        stopped = 0

        for instance in instances:
            if instance.state == 'running':
                running += 1
            elif instance.state == 'stopped':
                stopped += 1

            if instance.placement not in regions:
                regions[instance.placement] = {}

            if instance.state not in regions[instance.placement]:
                regions[instance.placement][instance.state] = 0

            regions[instance.placement][instance.state] += 1

        return {
            'instances': map(lambda t: marshal(t, instance_fields), instances),
            'regions': regions,
            'running': running,
            'stopped': stopped,
        }

    def delete(self):
        pass

    def post(self):
        instances = request.json['instances']
        for instance in instances:
            instanceLive = self._getInstance(instance['id'])
            if instanceLive.state != instance['state']:
                if instance['state'] == 'stop':
                    self._stop(instanceLive.id)
                elif instance['state'] == 'start':
                    self._start(instanceLive.id)

        return self.get()

    def _stop(self, id):
        amazon = Amazon()
        amazon.stop(id)

    def _start(self, id):
        amazon = Amazon()
        amazon.start(id)

    def _getInstance(self, id):
        amazon = Amazon()
        instances = amazon.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance


class InstanceApi(Resource):
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
        amazon = Amazon()
        amazon.stop(id)
        return self.get(id)

    def start(self, id):
        amazon = Amazon()
        amazon.start(id)
        return self.get(id)

    def delete(self, id):
        pass

    def _getInstance(self, id):
        amazon = Amazon()
        instances = amazon.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance
