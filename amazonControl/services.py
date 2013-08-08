#-=- encoding: utf-8 -=-
from flask.ext.restful import Resource, fields, marshal_with, marshal
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


class InstanceApi(Resource):
    @marshal_with(instance_fields)
    def get(self, id):
        amazon = Amazon()
        instances = amazon.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance
        pass

    def delete(self, id):
        pass
