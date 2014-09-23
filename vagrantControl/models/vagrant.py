# -=- encoding: utf-8 -=-

from vagrantControl import db
from vagrantControl import app
from vagrantControl.core import redis_conn, is_async
from vagrantControl.models.project import Project
from vagrantControl.models.host import Host
from vagrantControl.models.permission import ViewInstancePermission

import time
import slugify
from flask import request, session
from flask.ext.sqlalchemy import orm
from flask.ext.login import current_user
from rq import Queue, Connection


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
        self.instances = VagrantInstance.query.order_by('name')

    def get(self, instanceId):
        return VagrantInstance.query.get(int(instanceId))

    def find(self, instanceId=None, path=None):
        for instance in self.instances:
            if instance.id == instanceId or instance.path == path:
                return instance

        return None

    def get_all_instances(self):
        instances = filter(
            lambda instance: current_user.has_permission(ViewInstancePermission, instance.id),
            self.instances
        )
        return instances

    def create(self, request):
        if 'environment' in request:
            environment = request['environment']
        else:
            environment = ''

        project = Project.query.get(request['project'])
        host = Host.query.get(request['host'])
        instance = VagrantInstance(None, request['path'], request['name'],
                                   environment)
        if 'gitReference' in request:
            instance.git_reference = request['gitReference']

        instance.project = project
        instance.host = host
        db.session.add(instance)
        db.session.commit()

        if instance.git_reference:
            instance.clone()

        return instance

    def delete(self, instanceId):
        instance = VagrantInstance.query.get(instanceId)
        instance.delete()

    def provision(self, instanceId, machineName):
        instance = VagrantInstance.query.get(instanceId)
        return instance.provision(machineName)

    def stop(self, instanceId, machineName):
        instance = VagrantInstance.query.get(instanceId)
        return instance.stop(machineName)

    def start(self, instanceId, machineName):
        instance = VagrantInstance.query.get(instanceId)
        return instance.start(machineName)


class VagrantInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(256))
    name = db.Column(db.String(128))
    environment = db.Column(db.String(128))
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('project.id')
    )
    host_id = db.Column(
        db.Integer,
        db.ForeignKey('host.id')
    )
    git_reference = db.Column(db.String(128))

    def __init__(self, id, path, name, environment, git_reference=None):
        self.id = id
        self.path = path
        self.name = name
        self.environment = environment
        self.git_reference = git_reference
        # self.init_on_load()

    def __unicode__(self):
        return self._generatePath()

    def __str__(self):
        return self.__unicode__()

    def post(self):
        print request.json
        return self

    @orm.reconstructor
    def init_on_load(self):
        # self.status = self._status()
        # if 'running' in self.status:
        #     self.ip = self._ip()
        pass

    def _status(self):
        path = self._generatePath()

        results = self._submit_job(
            'status',
            path=path,
            host=self.host,
        )

        machines = self._parse_status(results)
        machinesFormatted = []
        for machine, value in machines.iteritems():
            machinesFormatted.append(
                {
                    'name': machine,
                    'status': value['state-human-short'],
                    # 'ip': value['ip']
                }
            )

        return machinesFormatted

    def _parse_status(self, results):
        results = results.split('\\n')
        results = results[1:-3]
        formatted = []
        item = []
        app.logger.debug(results)
        for result in results:
            result = result.replace('\\', ' ')
            if ',' in result and len(item) > 0:
                formatted.append(item)
                item = []

            if ',' in result:
                item = result.split(',')
                item[-1] = item[-1].replace('%!(VAGRANT_COMMA)', ',')
                formatted.append(item)
            else:
                result = result.replace('%!(VAGRANT_COMMA)', ',')
                item[-1] = item[-1] + result

        withoutTimestamp = []
        for item in formatted:
            withoutTimestamp.append(item[1:])

        machines = {}
        for item in withoutTimestamp:
            if item[0] not in machines:
                machines[item[0]] = {}

            machines[item[0]][item[1]] = item[2]

        # for machineName, value in machines.iteritems():
        #     machines[machineName]['ip'] = self._ip(machineName)

        app.logger.debug(machines)
        return machines

    def _ip(self, machineName):
        results = self._submit_job(
            'ip',
            path=self._generatePath(),
            machineName=machineName,
            host=self.host,
        )
        return results

    def _generatePath(self):
        path = self.path
        if self.git_reference is not None:
            return '/tmp/' + slugify.slugify(self.name)\
                + '/' + self.git_reference

        return path

    def start(self, machineName='default'):
        results = self._submit_job(
            'run',
            machineName=machineName,
            path=self._generatePath(),
            environment=self.environment,
            host=self.host,
        )

        return results

    def provision(self, machineName):
        results = self._submit_job(
            'provision',
            path=self._generatePath(),
            environment=self.environment,
            machineName=machineName,
            host=self.host,
        )
        return results

    def stop(self, machineName):
        results = self._submit_job(
            'stop',
            path=self._generatePath(),
            machineName=machineName,
            host=self.host,
        )
        return results

    def delete(self):
        self._submit_job(
            'destroy',
            path=self._generatePath(),
            host=self.host,
        )
        db.session.delete(self)
        db.session.commit()

    def clone(self):
        results = self._submit_job(
            'clone',
            path=self._generatePath(),
            git_address=self.project.git_address,
            git_reference=self.git_reference,
            host=self.host,
        )
        return results

    def _submit_job(self, action, **kwargs):
        with Connection():
            queue = Queue('high', connection=redis_conn)
            action = 'worker.{}'.format(action)
            job = queue.enqueue_call(func=action, timeout=600, kwargs=kwargs)

            # job = queue.enqueue(action, **kwargs)

            if action != 'status':
                if 'jobs' not in session:
                    session['jobs'] = []

                session['jobs'].append(
                    {
                        'jobId': job.id,
                        'instanceId': self.id,
                        'userId': current_user.id,
                        'action': action
                    }
                )
                if is_async() is False:
                    while job.result is None:
                        time.sleep(0.5)

        return job.result
