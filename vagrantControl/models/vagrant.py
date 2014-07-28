# -=- encoding: utf-8 -=-

from vagrantControl import db
from vagrantControl.core import redis_conn, is_async
from vagrantControl.settings import ETH

import re
import time
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
        return self.instances

    def create(self, request):
        if 'environment' in request:
            environment = request['environment']
        else:
            environment = ''

        instance = VagrantInstance(None, request['path'], request['name'],
                                   environment)
        db.session.add(instance)
        db.session.commit()

        return instance

    def delete(self, instanceId):
        instance = VagrantInstance.query.get(instanceId)
        instance.delete()

    def provision(self, instanceId):
        instance = VagrantInstance.query.get(instanceId)
        return instance.provision()

    def stop(self, instanceId):
        instance = VagrantInstance.query.get(instanceId)
        return instance.stop()

    def start(self, instanceId, provider):
        instance = VagrantInstance.query.get(instanceId)
        return instance.start(provider)


class VagrantInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(256))
    name = db.Column(db.String(128))
    environment = db.Column(db.String(128))
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('project_id')
    )

    def __init__(self, id, path, name, environment):
        self.id = id
        self.path = path
        self.name = name
        self.environment = environment
        # self.init_on_load()

    def __unicode__(self):
        return self.path

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
        results = self._submit_job('status', path=self.path)
        results = re.findall(r'.*states:\\n\\n(.*)\\n\\nTh.*', results, re.M)
        results = results[0].split('\\n')
        # We remove the whitespace in between each word
        results = [' '.join(result.split()) for result in results]
        return results

    def _ip(self):
        results = self._submit_job('ip', path=self.path)
        return results

    def start(self, provider=None):
        results = self._submit_job(
            'run',
            path=self.path,
            eth=ETH,
            environment=self.environment,
            provider=provider
        )
        return results

    def provision(self):
        results = self._submit_job(
            'provision',
            path=self.path,
            environment=self.environment
        )
        return results

    def stop(self):
        results = self._submit_job('stop', path=self.path)
        return results

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        self._submit_job('destroy', path=self.path)

    def _submit_job(self, action, **kwargs):
        with Connection():
            queue = Queue('high', connection=redis_conn)
            action = 'worker.{}'.format(action)
            job = queue.enqueue_call(func=action, timeout=600, kwargs=kwargs)

            # job = queue.enqueue(action, **kwargs)

            if action != 'status':
                if 'jobs' not in session:
                    session['jobs'] = []

                # app.logger.debug(job.id)
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
