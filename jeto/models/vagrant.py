# -=- encoding: utf-8 -=-

from jeto import db
from jeto import app
from jeto.settings import PROJECT_BASEPATH
from jeto.core import redis_conn, is_async
from jeto.models.project import Project
from jeto.models.host import Host
from jeto.models.permission import ViewInstancePermission
from jeto.models.auditlog import auditlog

import time
import slugify
import json
import ansiconv
from flask import request
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
            lambda instance: current_user.has_permission(
                ViewInstancePermission,
                instance.id
            ),
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
        instance.git_reference = request.get('gitReference')
        instance.archive_url = request.get('archive_url')

        instance.project = project
        instance.host = host
        db.session.add(instance)
        db.session.commit()

        if instance.git_reference:
            instance.clone()
        elif instance.archive_url:
            instance.extract()

        return instance

    def sync(self, instanceId):
        instance = VagrantInstance.query.get(instanceId)
        return instance.sync()

    def delete(self, instanceId):
        instance = VagrantInstance.query.get(instanceId)
        auditlog(
            current_user,
            'delete instance',
            instance)
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
    archive_url = db.Column(db.String(256))

    def __init__(self, id, path, name, environment,
                 git_reference=None, archive_url=None):
        self.id = id
        self.path = path
        self.name = name
        self.environment = environment
        self.git_reference = git_reference
        self.archive_url = archive_url
        # self.init_on_load()

    def __unicode__(self):
        return '{} : {} : {}'.format(
            self.name,
            self.status,
            self._generatePath()
        )

    def __str__(self):
        return self.__unicode__()

    def post(self):
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
            environment=self.environment,
        )

        machines, jeto_infos, scripts, date_commit = self._parse_status(results)
        machinesFormatted = []
        for machine, value in machines.iteritems():
            app.logger.debug(value)
            if 'state-human-short' in value:
                val = value['state-human-short']
            elif 'error-exit' in value:
                val = value['error-exit'] # Vagrant is not ready yet
            else:
                val = 'Something went wrong'

            machinesFormatted.append(
                {
                    'name': machine,
                    'status': val,
                    # 'ip': value['ip']
                }
            )

        return machinesFormatted, jeto_infos, scripts, date_commit

    def _parse_status(self, results):
        results = json.loads(results)

        date_commit = results.get('date_commit', None)

        jeto_infos = results.get('jeto_infos')
        scripts = None
        if jeto_infos:
            scripts = jeto_infos.get('scripts', None)
            if scripts:
                del jeto_infos['scripts']

        results = results.get('vagrant', 'Something went wrong\n')
        machines = {}
        if results is not None:
            results = results.split('\n')
            # Vagrant returns 5 lines, the first one being #BEGIN# and
            # the last line being #END#, we want everything else
            results = results[1:-3]
            formatted = []
            item = []
            for result in results:
                # Clean up
                result = result.replace('\\', ' ')

                if ',' in result and len(item) > 0:
                    formatted.append(item)
                    item = []

                # Each field is comma seperated
                if ',' in result:
                    item = result.split(',')
                    # !(VAGRANT_COMMA) is a real comma, but escaped by vagrant
                    item[-1] = item[-1].replace('%!(VAGRANT_COMMA)', ',')
                    formatted.append(item)
                else:
                    # !(VAGRANT_COMMA) is a real comma, but escaped by vagrant
                    result = result.replace('%!(VAGRANT_COMMA)', ',')
                    if len(item):
                        item[-1] = item[-1] + result


            withoutTimestamp = []
            for item in formatted:
                withoutTimestamp.append(item[1:])

            for item in withoutTimestamp:
                if item[0] not in machines:
                    machines[item[0]] = {}

                if len(item) >= 3:
                    machines[item[0]][item[1]] = item[2]

        return (machines, jeto_infos, scripts, date_commit)

    def _ip(self, machineName):
        results = self._submit_job(
            'ip',
            path=self._generatePath(),
            machineName=machineName,
            host=self.host,
            environment=self.environment,
        )
        return results

    def _generatePath(self):
        path = self.path
        if self.git_reference:
            return PROJECT_BASEPATH + \
                slugify.slugify(self.project.name) +\
                '/' + \
                slugify.slugify(self.name) + \
                '/' + \
                self.git_reference
        elif self.archive_url:
            return PROJECT_BASEPATH + \
                slugify.slugify(self.project.name) +\
                '/' + \
                slugify.slugify(self.name) + \
                '/' + \
                'tgz'

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
            environment=self.environment,
            machineName=machineName,
            host=self.host,
        )
        return results

    def delete(self):
        self._submit_job(
            'destroy',
            path=self._generatePath(),
            environment=self.environment,
            host=self.host,
        )
        db.session.delete(self)
        db.session.commit()

    def extract(self):
        results = self._submit_job(
            'extract',
            path=self._generatePath(),
            archive_url=self.archive_url,
            host=self.host,
        )
        return results

    def rsync(self):
        results = self._submit_job(
            'rsync',
            path=self._generatePath(),
            host=self.host,
        )
        return results

    def sync(self):
        results = self._submit_job(
            'sync',
            path=self._generatePath(),
            git_reference=self.git_reference,
        )
        return results

    def clone(self):
        results = self._submit_job(
            'clone',
            path=self._generatePath(),
            git_address=self.project.git_address,
            git_reference=self.git_reference,
            host=self.host,
        )
        return results

    def runScript(self, script, machineName='default'):
        results = self._submit_job(
            'run_script',
            path=self._generatePath(),
            host=self.host,
            environment=self.environment,
            machineName=machineName,
            script=script,
        )
        return results

    def _submit_job(self, action, **kwargs):
        with Connection():
            queue = Queue('high', connection=redis_conn)
            action = 'worker.{}'.format(action)
            job = queue.enqueue_call(
                func=action,
                timeout=1200,
                job_id=str(time.time()),
                kwargs=kwargs,
            )
            if action != 'worker.status':
                redis_conn.zadd(
                    'jobs:{}'.format(self.id),
                    str(current_user.id),
                    job.id,
                )

            if is_async() is False:
                while job.result is None:
                    time.sleep(0.5)

        return job.result
