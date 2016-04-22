#!/usr/bin/env python
# -=- encoding: utf-8 -=-
from unittest import TestCase
from flask.ext.webtest import TestApp
from jeto import app, db
from jeto import services
import jeto
from mock import patch, Mock, MagicMock

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

class TestTeamsAPI(TestCase):

    def setUp(self):
        jeto.services.projects.auditlog = MagicMock()
        jeto.services.hosts.auditlog = MagicMock()
        jeto.services.instances.auditlog = MagicMock()
        jeto.models.vagrant.VagrantInstance._submit_job = Mock()
        jeto.models.vagrant.VagrantInstance._status = Mock()
        jeto.models.vagrant.VagrantInstance._status.return_value = [{"name": "www", "status": "Not created", "ip": ""}, "", "", "2016-04-22"]
        self.app = app
        self.webtest = TestApp(self.app, db=db, use_session_scopes=True)
        db.create_all()

    def tearDown(self):
        db.drop_all()

    @patch('jeto.services.current_user')
    def test_get_empty(self, current_user):
        '''
        If the database have none teams
        '''
        current_user.is_authenticated = Mock(return_value=True)
        r = self.webtest.get('/api/instances')
        self.assertEqual(r.json, [])

    @patch('jeto.services.current_user')
    @patch('jeto.services.projects.current_user')
    @patch('jeto.services.hosts.current_user')
    @patch('jeto.models.vagrant.current_user')
    def test_general(self, current_user, current_user_proj, current_user_host, current_user_vagrant):
        instance = {
            "path": "",
            "name": "My instance",
            "environment": "QA",
            "gitReference": "master",
            "archive_url": "",
            "project": "1",
            "host": "1"
        }
        instance_created = {
            "id":  "1",
            "path": "",
            "name": "My instance",
            "environment": "QA",
            "git_reference": "master",
            "archive_url": "",
            "machines": [],
            "jeto_infos": "",
            "project": {
                "id":  "1",
                "name": "My project",
                "base_path": None,
                "git_address": "https://github.com/PierrePaul/phpquebec-2014-09-04.git",
            },
            "host": {
                "id":  "1",
                "name": "Original name",
                "params": "",
                "provider": ""
            }
        }

        project = {
            "id":  None,
            "name": "My project",
            "git_address": "https://github.com/PierrePaul/phpquebec-2014-09-04.git"
        }
        project_created = {
            "id":  "1",
            "name": "My project",
            "base_path": None,
            "git_address": "https://github.com/PierrePaul/phpquebec-2014-09-04.git",
            "teams": [],
            "instances": []
        }
        host = {
            "id":  "1",
            "name": "Original name",
            "params": "",
            "provider": ""
        }

        current_user.is_authenticated = Mock(return_value=True)
        current_user.is_admin = Mock(return_value=True)
        current_user_proj.is_admin = Mock(return_value=True)
        current_user_host.has_permission = Mock(return_value=True)
        current_user_vagrant.has_permission = Mock(return_value=True)
        r = self.webtest.post_json('/api/projects', project)
        self.assertEqual(r.json, project_created)
        r = self.webtest.post_json('/api/host', host)
        self.assertEqual(r.json, host)
        self.assertTrue(jeto.services.hosts.auditlog.called)
        r = self.webtest.get('/api/host/1')
        self.assertEqual(r.json, host)
        r = self.webtest.post_json('/api/instance', instance)
        self.assertEqual(r.json, instance_created)
        self.assertTrue(jeto.models.vagrant.VagrantInstance._submit_job.called)
        r = self.webtest.get('/api/instance/1')
        instance_created["date_commit"] = '2016-04-22'
        instance_created["scripts"] = ""
        instance_created["machines"] = [{'status': 'Not created', 'ip': '', 'name': 'www'}]
        self.assertEqual(r.json, instance_created)
        r = self.webtest.get('/api/instances')
        del instance_created["date_commit"]
        del instance_created["scripts"]
        instance_created["machines"] = []
        self.assertEqual(r.json, [instance_created])
        r = self.webtest.delete('/api/instance/1')
        self.assertTrue(r.status, 200)
        r = self.webtest.get('/api/instance/1', expect_errors=True)
        self.assertEqual(r.status, "404 NOT FOUND")
        r = self.webtest.get('/api/instances')
        self.assertEqual(r.json, [])

    pass
