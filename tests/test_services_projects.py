#!/usr/bin/env python
# -=- encoding: utf-8 -=-
from unittest import TestCase
from unittest import main
from flask.ext.webtest import TestApp
from jeto import app, db
from jeto.models.project import Project
from jeto import services
import jeto
import flask_restful
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
    def test_general(self, current_user):
        project = {
            "id":  None,
            "name": "My project"
        }
        project_created = {
            "id":  "1",
            "name": "My project",
            "base_path": None,
            "git_address": None
        }

        current_user.is_authenticated = Mock(return_value=True)
        current_user.is_admin = Mock(return_value=True)
        r = self.webtest.post_json('/api/projects', project)
        app.logger.debug(r.json)
        self.assertEqual(r.json, project_created)
        self.assertTrue(jeto.services.projects.auditlog.called)
        r = self.webtest.get('/api/projects/1')
        self.assertEqual(r.json, project_created)
        r = self.webtest.get('/api/projects')
        self.assertEqual(r.json, [project_created])

    pass
