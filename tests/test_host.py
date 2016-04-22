#!/usr/bin/env python
# -=- encoding: utf-8 -=-
from unittest import TestCase
from flask.ext.webtest import TestApp
from jeto import app, db
from jeto import services
import jeto
from mock import patch, Mock, MagicMock

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

class TestHostsAPI(TestCase):

    def setUp(self):
        jeto.services.hosts.auditlog = MagicMock()
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
        r = self.webtest.get('/api/hosts')
        self.assertEqual(r.json, [])

    @patch('jeto.services.current_user')
    @patch('jeto.services.hosts.current_user')
    def test_general(self, current_user, current_user_host):
        host = {
            "id":  "1",
            "name": "Original name",
            "params": "",
            "provider": ""
        }
        host_created = {
            "id":  "1",
            "name": "Original name",
            "params": "",
            "provider": ""
        }

        current_user.is_authenticated = Mock(return_value=True)
        current_user.is_admin = Mock(return_value=True)
        current_user_host.has_permission = Mock(return_value=True)
        r = self.webtest.post_json('/api/host', host)
        self.assertEqual(r.json, host_created)
        self.assertTrue(jeto.services.hosts.auditlog.called)
        r = self.webtest.get('/api/host/1')
        self.assertEqual(r.json, host_created)
        r = self.webtest.get('/api/hosts')
        self.assertEqual(r.json, [host_created])
        host['name'] = "New name"
        host_created['name'] = "New name"
        r = self.webtest.put_json('/api/host/1', host)
        self.assertEqual(r.json, host_created)
        r = self.webtest.get('/api/host/1')
        self.assertEqual(r.json, host_created)
        r = self.webtest.get('/api/hosts')
        self.assertEqual(r.json, [host_created])
        r = self.webtest.delete('/api/host/1')
        self.assertTrue(r.status, 200)
        r = self.webtest.get('/api/host/1', expect_errors=True)
        self.assertEqual(r.status, "404 NOT FOUND")
        r = self.webtest.get('/api/hosts')
        self.assertEqual(r.json, [])

    pass
