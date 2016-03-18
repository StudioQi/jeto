#!/usr/bin/env python
# -=- encoding: utf-8 -=-
from unittest import TestCase
from unittest import main
from flask.ext.webtest import TestApp
from jeto import app, db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

class TestTeamsAPI(TestCase):
    def setUp(self):
        self.app = app
        self.webtest = TestApp(self.app, db=db, use_session_scopes=True)
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def test_post(self, request):


    pass


if __name__ == '__main__':
    main()
