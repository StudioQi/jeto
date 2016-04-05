#!/usr/bin/env python
# -=- encoding: utf-8 -=-
from unittest import TestCase
from unittest import main
from flask.ext.webtest import TestApp
from jeto import app, db
from jeto.models.team import Team
from jeto import services
import jeto
import flask_restful
from mock import patch, Mock, MagicMock

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

class TestTeamsAPI(TestCase):

    def setUp(self):
        jeto.services.teams.auditlog = MagicMock()
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
        r = self.webtest.get('/api/teams')
        self.assertEqual(r.json, [])

    @patch('jeto.services.current_user')
    def test_general(self, current_user):
        team = {
            "id":  1,
            "name": "Original name",
            "users": []
        }
        team_created = {
            "id":  "1",
            "name": "Original name",
            "users": [],
            "permissions_grids": []
        }

        current_user.is_authenticated = Mock(return_value=True)
        current_user.is_admin = Mock(return_value=True)
        r = self.webtest.post_json('/api/teams', team)
        self.assertEqual(r.json, team_created)
        self.assertTrue(jeto.services.teams.auditlog.called)
        r = self.webtest.get('/api/teams/1')
        self.assertEqual(r.json, team_created)
        r = self.webtest.get('/api/teams')
        self.assertEqual(r.json, [team_created])
        team['name'] = "New name"
        team_created['name'] = "New name"
        r = self.webtest.put_json('/api/teams/1', team)
        self.assertEqual(r.json, team_created)
        r = self.webtest.get('/api/teams/1')
        self.assertEqual(r.json, team_created)
        r = self.webtest.get('/api/teams')
        self.assertEqual(r.json, [team_created])
        r = self.webtest.delete('/api/teams/1')
        self.assertTrue(r.status, 200)
        #r = self.webtest.get('/api/teams/1')
        #app.logger.debug(r)
        #self.assertEqual(r.json, None)
        r = self.webtest.get('/api/teams')
        self.assertEqual(r.json, [])
        #self.assertEqual(r.status, 404)

    pass