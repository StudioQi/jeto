# -=- encoding: utf-8 -=-

from jeto import db, app
from jeto.core import redis_conn, is_async
from jeto.models.project import Project
from jeto.models.host import Host
from jeto.models.permission import ViewInstancePermission
from jeto.models.auditlog import auditlog

import time
import slugify
import json
from rq import Queue, Connection
from flask import request, abort
from flask_login import current_user

class VagrantBackend():

    def get(self, instance_id):
        instance = VagrantInstance.query.get_or_404(int(instance_id))
        if(current_user.has_permission(
                ViewInstancePermission,
                instance.id
            )):
            return instance
        else:
            abort(403)

    def get_all_instances(self):
        instances = filter(
            lambda instance: current_user.has_permission(
                ViewInstancePermission,
                instance.id
            ),
            VagrantInstance.query.order_by('name')
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
            # TODO: Add an exception if the clone fail
            instance.clone()
        elif instance.archive_url:
            # TODO: Add an exception if the extract fail
            instance.extract()

        return instance

    @staticmethod
    def sync(instance_id):
        instance = VagrantInstance.query.get(instance_id)
        return instance.sync()

    @staticmethod
    def delete(instance_id):
        instance = VagrantInstance.query.get(instance_id)
        instance.delete()

    @staticmethod
    def provision(instance_id, machine_name):
        instance = VagrantInstance.query.get(instance_id)
        return instance.provision(machine_name)

    @staticmethod
    def stop(instance_id, machine_name):
        instance = VagrantInstance.query.get(instance_id)
        return instance.stop(machine_name)

    @staticmethod
    def start(instance_id, machine_name):
        instance = VagrantInstance.query.get(instance_id)
        return instance.start(machine_name)


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
            self._status,
            self._generate_path()
        )

    def __str__(self):
        return self.__unicode__()

    def post(self):
        return self

    def _status(self):
        path = self._generate_path()

        results = self._submit_job(
            'status',
            path=path,
            host=self.host,
            environment=self.environment,
        )

        machines, jeto_infos, scripts, date_commit = VagrantInstance.parse_status(results)
        machines_formatted = []
        for machine, value in machines.iteritems():
            if 'state-human-short' in value:
                val = value['state-human-short']
            elif 'error-exit' in value:
                val = value['error-exit']  # Vagrant is not ready yet
            else:
                val = 'Something went wrong'

            machines_formatted.append(
                {
                    'name': machine,
                    'status': val,
                    # 'ip': value['ip']
                }
            )

        return machines_formatted, jeto_infos, scripts, date_commit

    @staticmethod
    def parse_status(results):
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

                # Each field is comma separated
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

            without_timestamp = []
            for item in formatted:
                without_timestamp.append(item[1:])

            for item in without_timestamp:
                if item[0] not in machines:
                    machines[item[0]] = {}

                if len(item) >= 3:
                    machines[item[0]][item[1]] = item[2]

        return machines, jeto_infos, scripts, date_commit

    def _ip(self, machine_name):
        results = self._submit_job(
            'ip',
            path=self._generate_path(),
            machine_name=machine_name,
            host=self.host,
            environment=self.environment,
        )
        return results

    def _generate_path(self):
        path = self.path
        if self.git_reference:
            return app.config.get('PROJECT_BASEPATH') + \
                slugify.slugify(self.project.name) +\
                '/' + \
                slugify.slugify(self.name) + \
                '/' + \
                self.git_reference
        elif self.archive_url:
            return app.config.get('PROJECT_BASEPATH') + \
                slugify.slugify(self.project.name) +\
                '/' + \
                slugify.slugify(self.name) + \
                '/' + \
                'tgz'

        return path

    def start(self, machine_name='default'):
        results = self._submit_job(
            'run',
            machine_name=machine_name,
            path=self._generate_path(),
            environment=self.environment,
            host=self.host,
        )

        return results

    def provision(self, machine_name):
        results = self._submit_job(
            'provision',
            path=self._generate_path(),
            environment=self.environment,
            machine_name=machine_name,
            host=self.host,
        )
        return results

    def stop(self, machine_name):
        results = self._submit_job(
            'stop',
            path=self._generate_path(),
            environment=self.environment,
            machine_name=machine_name,
            host=self.host,
        )
        return results

    def delete(self):
        self._submit_job(
            'destroy',
            path=self._generate_path(),
            environment=self.environment,
            host=self.host,
        )
        db.session.delete(self)
        db.session.commit()

    def extract(self):
        results = self._submit_job(
            'extract',
            path=self._generate_path(),
            archive_url=self.archive_url,
            host=self.host,
        )
        return results

    def rsync(self):
        results = self._submit_job(
            'rsync',
            path=self._generate_path(),
            host=self.host,
        )
        return results

    def sync(self):
        results = self._submit_job(
            'sync',
            path=self._generate_path(),
            git_reference=self.git_reference,
        )
        return results

    def clone(self):
        results = self._submit_job(
            'clone',
            path=self._generate_path(),
            git_address=self.project.git_address,
            git_reference=self.git_reference,
            host=self.host,
        )
        return results

    def run_script(self, script, machine_name='default'):
        """
        Run a script as specified in the jeto.json file
        :param script: Name definied in jeto.json
        :param machine_name: Name for the machine
        :return:
        """
        results = self._submit_job(
            'run_script',
            path=self._generate_path(),
            host=self.host,
            environment=self.environment,
            machine_name=machine_name,
            script=script,
        )
        return results

    def _submit_job(self, action, **kwargs):
        """
        Send a job to the queue manager
        :param action:
        :param kwargs:
        :return:
        """
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
                redis_conn.hmset(
                    'jobs:{}'.format(self.id),
                    {job.id: str(current_user.id)}
                )

            if is_async() is False:
                while job.result is None:
                    time.sleep(0.5)
            else:
                return job.id

        return job.result
