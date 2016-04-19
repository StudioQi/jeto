#!/usr/bin/env python
# -=- encoding: utf-8 -=-
from unittest import TestCase
from flask.ext.webtest import TestApp
from jeto import app, db
from jeto import services
import jeto
from mock import patch, Mock, MagicMock

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

class TestProjectsAPI(TestCase):

    def setUp(self):
        jeto.services.projects.auditlog = MagicMock()
        self.app = app
        self.webtest = TestApp(self.app, db=db, use_session_scopes=True)
        db.create_all()

    def tearDown(self):
        db.drop_all()

    @patch('jeto.services.current_user')
    def test_get_empty(self, current_user):
        '''
        If the database have none project
        '''
        current_user.is_authenticated = Mock(return_value=True)
        r = self.webtest.get('/api/projects')
        self.assertEqual(r.json, [])

    @patch('jeto.services.current_user')
    @patch('jeto.services.projects.current_user')
    def test_general(self, current_user, current_user_serv):
        project = {
            "id":  None,
            "name": "My project"
        }
        project_created = {
            "id":  "1",
            "name": "My project",
            "base_path": None,
            "git_address": None,
            "teams": [],
            "instances": []
        }

        current_user.is_authenticated = Mock(return_value=True)
        current_user.is_admin = Mock(return_value=True)
        current_user_serv.is_admin = Mock(return_value=True)
        r = self.webtest.post_json('/api/projects', project)
        project = r.json
        self.assertEqual(r.json, project_created)
        self.assertTrue(jeto.services.projects.auditlog.called)
        r = self.webtest.get('/api/projects/1')
        self.assertEqual(r.json, project_created)
        r = self.webtest.get('/api/projects')
        self.assertEqual(r.json, [project_created])
        project['name'] = "My project rebuild"
        project_created['name'] = "My project rebuild"
        r = self.webtest.put_json('/api/projects/1', project)
        self.assertEqual(r.json, project_created)
        self.assertTrue(jeto.services.projects.auditlog.called)
        r = self.webtest.get('/api/projects/1')
        self.assertEqual(r.json, project_created)
        r = self.webtest.delete('/api/projects/1')
        self.assertTrue(r.status, 200)
        r = self.webtest.get('/api/projects/1', expect_errors=True)
        self.assertEqual(r.status, "404 NOT FOUND")
        r = self.webtest.get('/api/projects')
        self.assertEqual(r.json, [])

    pass
