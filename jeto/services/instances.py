from flask import request, abort

from flask_restful import Resource, fields, marshal
from flask_login import current_user

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

        return [marshal(instance, instance_fields) for instance in instances]

    def delete(self):
        instance_id = int(request.json['id'])
        self.backend.delete(instance_id)

    def post(self):
        query = request.get_json()
        instance_id = query.get('id')
        if instance_id:
            instance_id = int(instance_id)
            instance = self.backend.get(instance_id)

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

        return marshal(instance, instance_fields);

    def _sync(self, id):
        self.backend.sync(id)

    def _stop(self, id):
        self.backend.stop(id)

    def _start(self, id):
        self.backend.start(id)

    def _get_instance(self, id):
        instances = self.backend.get_all_instances()
        for instance in instances:
            if instance.id == id:
                return instance


class InstanceApi(Resource):
    backend = None

    def __init__(self):
        self.backend = VagrantBackend()

    def get(self, id, machine_name=None):
        instance = self._get_instance(id)
        if machine_name is None:
            instance.status, jeto_infos, scripts, date_commit = instance._status()
        else:
            return {'ip': instance._ip(machine_name)}

        instance_json = marshal(instance, instance_fields)
        instance_json['date_commit'] = date_commit
        instance_json['jeto_infos'] = jeto_infos
        instance_json['scripts'] = scripts
        return instance_json

    def post(self, id):
        instance = self._get_instance(id) or abort(404)

        changed = False
        query = request.get_json()
        if 'name' in query:
            if query['name'] != instance.name:
                instance.name = query['name']
                changed = True

        if changed:
            instance.save()

        machine_name = ''
        if 'machine' in query:
            machine_name = query['machine']

        state = query.get('state')
        permission = states.get(state)
        if permission:
            if current_user.has_permission(permission, id):
                if state == 'runScript':
                    instance.runScript(query.get('script'), machine_name)
                elif state == 'rsync':
                    instance.rsync()
                elif state == 'sync':
                    instance.sync()
                else:
                    getattr(self, state)(id, machine_name)
            else:
                abort(403)

    def provision(self, id, machine_name):
        return self.backend.provision(id, machine_name)

    def stop(self, id, machine_name):
        return self.backend.stop(id, machine_name)

    def start(self, id, machine_name):
        return self.backend.start(id, machine_name)

    def sync(self, id):
        return self.backend.sync(id)

    def delete(self, id):
        instance_id = int(id)
        return self.backend.delete(instance_id)

    def _get_instance(self, id):
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
            try:
                # job = Job.fetch(str(command_id), connection=redis_conn)
                job = redis_conn.hgetall('rq:job:{}'.format(command_id))
                job.pop('data', None)
                job.pop('description', None)

                console = redis_conn.get('{}:console'.format(command_id)) or ''
                job.update(
                        {'id': command_id,
                         'result': u'{}'.format(repr(job.get('result', ''))),
                         'console': console})
                return job

            except Exception as e:
                print(e.message)
                abort(400)
        # find redis jobs for the instance
        jobs_key = 'jobs:{}'.format(instance_id)
        jobs = redis_conn.hkeys(jobs_key)
        # sort by jobid/time most recent first
        jobs.sort(reverse=True)
        return jobs

    def post(self, instance_id):
        instance = self._get_instance(instance_id) or abort(404)

        query = request.get_json()
        # force async
        request.json['async'] = True

        machine_name = query.get('machine', "")

        action = query.get('action')
        permission = states.get(action)
        job_id = None
        if permission:
            if current_user.has_permission(permission, instance_id):
                if action == 'runScript':
                    job_id = instance.runScript(
                        query.get('script'), machine_name)
                elif action == 'rsync':
                    job_id = instance.rsync()
                elif action == 'sync':
                    job_id = instance.sync()
                else:
                    job_id = getattr(self, action)(instance_id, machine_name)
            else:
                abort(403)

        if job_id is None:
            abort(500)

        console = redis_conn.get('{}:console'.format(job_id)) or ''
        return {
            'id': job_id,
            'console': console
        }
