from flask import request, abort

from flask.ext.restful import Resource, fields, marshal
from flask.ext.login import current_user

from jeto import app
from rq.job import Job
from jeto.core import redis_conn

from jeto.services.hosts import host_fields
from jeto.services import project_wo_instance_fields

from jeto.models.vagrant import VagrantBackend
from jeto.models.auditlog import auditlog
from jeto.models.permission import ProvisionInstancePermission,\
    StopInstancePermission, StartInstancePermission,\
    RunScriptInstancePermission, SyncInstancePermission, \
    RSyncInstancePermission

states = {
    'stop': StopInstancePermission,
    'start': StartInstancePermission,
    'provision': ProvisionInstancePermission,
    'runScript': RunScriptInstancePermission,
    'rsync': RSyncInstancePermission,
    'sync': SyncInstancePermission
}


status_fields = {
    'name': fields.String,
    'status': fields.String,
    'ip': fields.String,
}

instance_fields = {
    'id': fields.String,
    'name': fields.String,
    'path': fields.String,
    'archive_url': fields.String,
    'git_reference': fields.String,
    'status': fields.Nested(status_fields),
    'environment': fields.String,
    'project': fields.Nested(project_wo_instance_fields),
    'host': fields.Nested(host_fields),
    'jeto_infos': fields.List(fields.String),
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
        query = request.get_json()
        instanceId = query.get('id')
        if instanceId:
            instanceId = int(instanceId)
            instance = self.backend.get(instanceId)

            auditlog(
                current_user,
                '{} instance'.format(query.get('state', 'unknown')),
                instance,
                request_details=request.get_json())
            if 'start' in query.get('state', ''):
                provider = query['state'].replace('start-', '')
                instance.start(provider)

            elif query.get('state') == 'stop':
                instance.stop()
            elif query.get('state') == 'sync':
                instance.sync()

        elif query.get('state') == 'create':
            instance = self.backend.create(query)
        else:
            return self.get()

        return {
            'instance': marshal(instance, instance_fields),
        }

    def _sync(self, id):
        self.backend.sync(id)

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

    def get(self, id, machineName=None):
        instance = self._getInstance(id)
        jeto_infos = None
        if machineName is None:
            instance.status, jeto_infos, scripts, date_commit = instance._status()
            # instance.jeto_infos = json.dumps(instance.jeto_infos)
        else:
            # app.logger.debug(instance._ip(machineName))
            return {'ip': instance._ip(machineName)}

        instance_json = marshal(instance, instance_fields)
        instance_json['date_commit'] = date_commit
        instance_json['jeto_infos'] = jeto_infos
        instance_json['scripts'] = scripts
        return instance_json

    def post(self, id):
        instance = self._getInstance(id) or abort(404)

        changed = False
        query = request.get_json()
        if 'name' in query:
            if query['name'] != instance.name:
                instance.name = query['name']
                changed = True

        if changed:
            instance.save()

        if 'machine' in query:
            machineName = query['machine']

        state = query.get('state')
        permission = states.get(state)
        if permission:
            if current_user.has_permission(permission, id):
                if state == 'runScript':
                    instance.runScript(query.get('script'), machineName)
                elif state == 'rsync':
                    instance.rsync()
                elif state == 'sync':
                    instance.sync()
                else:
                    getattr(self, state)(id, machineName)
            else:
                abort(403)

    def provision(self, id, machineName):
        return self.backend.provision(id, machineName)

    def stop(self, id, machineName):
        return self.backend.stop(id, machineName)

    def start(self, id, machineName):
        return self.backend.start(id, machineName)

    def sync(self, id):
        return self.backend.sync(id)

    def delete(self, id):
        instanceId = int(id)
        return self.backend.delete(instanceId)

    def _getInstance(self, id):
        instances = self.backend.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance


class CommandApi(InstanceApi):
    """sends commands to instances"""
    def get(self, instance_id, command_id=None):
        """Get a list of commands in queue for the instance
        or the specified command states+output"""
        if command_id is not None:
            job = Job.fetch(str(command_id), connection=redis_conn)
            return job.status
        # find redis jobs for the instance
        jobs_key = 'jobs:{}'.format(instance_id)
        jobs = redis_conn.hkeys(jobs_key)
        # sort by jobid/time most recent first
        jobs.sort(reverse=True)
        return jobs

    def post(self, instance_id):
        instance = self._getInstance(instance_id) or abort(404)

        query = request.get_json()
        # force async
        request.json['async'] = True

        machineName = query.get('machine', "")

        action = query.get('action')
        permission = states.get(action)
        if permission:
            if current_user.has_permission(permission, instance_id):
                if action == 'runScript':
                    return instance.runScript(query.get('script'), machineName)
                elif action == 'rsync':
                    return instance.rsync()
                elif action == 'sync':
                    return instance.sync()
                else:
                    return getattr(self, action)(instance_id, machineName)
            else:
                abort(403)
