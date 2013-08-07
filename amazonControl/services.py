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
        return {'instances': map(lambda t: marshal(t, instance_fields),
                instances)}

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
