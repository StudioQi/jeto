#!/usr/bin/env python
# -=- encoding: utf-8 -=-
from unittest import TestCase
from unittest import main
from mock import patch
from common import mock_modules
from json import dumps


@patch.dict('sys.modules', mock_modules)
#@patch('jeto.db')
@patch('jeto.services.SSL')
@patch("jeto.services.req")
@patch("jeto.services.request")
@patch("jeto.services.json")
class TestSSLApi(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('jeto.services.DomainController')
    def test_delete(self, dc, json, request, requests, ssl_model):
        """delete a certificate"""
        from jeto import db
        json.dumps.side_effect = lambda *args: dumps(*args)
        name = "what a nice name"
        domaincontroller = "my domaincontroller"
        cert_value = "347D34DB33F175600D"
        query_content = {
            "name": name,
            "domaincontroller": domaincontroller,
            "value": cert_value
            }
        request.get_json.return_value = query_content
        dc.query.get.return_value.url = "http://test"
        from jeto.services import SSLApi
        # mock a SqlAlchemy query result
        key_obj = type('SSLModel', (object,),
                       {'id': '123',
                        'name': name,
                        'domaincontroller': type(
                            'DCModel',
                            (object,),
                            {'url': 'http://test'})
                        })

        ssl_model.query.get.side_effect = lambda *args: key_obj
        SSLApi().delete('123')
        # remove from the db
        ssl_model.query.get.assert_called_with('123')
        db.session.delete.assert_called_with(key_obj)
        # forward to nginx-api
        requests.delete.assert_called_with(
            "http://test",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'},
            data=dumps(
                {"name": name}
            ))

    # patch passes mocks from bottom to top
    def test_get(self, json, request, requests, ssl_model):
        """Get a list of available certificates"""
        # FIXME: find a way to not import at every test (code duplication)
        from jeto.services import SSLApi
        res = SSLApi().get()
        ssl_model.query.all.assert_called_with()
        self.assertEquals(res, ssl_model.query.all())
        res = SSLApi().get('1')
        ssl_model.query.filter_by.assert_called_with(domaincontroller='1')
        self.assertEquals(res, ssl_model.query.filter_by(domaincontroller='1'))

    @patch('jeto.services.DomainController')
    def test_post(self, dc, json, request, requests, ssl_model):
        """Create a certificate"""
        # FIXME: actuellement 'post' écrase
        #   faut-il refuser si une clef existe ?
        from jeto import db
        json.dumps.side_effect = lambda *args: dumps(*args)
        name = "what a nice name"
        domaincontroller = "my domaincontroller"
        cert_value = "347D34DB33F175600D"
        query_content = {
            "name": name,
            "domaincontroller": domaincontroller,
            "value": cert_value
            }
        request.get_json.return_value = query_content
        dc.query.get.return_value.url = "http://test"
        from jeto.services import SSLApi
        SSLApi().post()
        # ensure we created an SSL object in DB
        ssl_model.assert_called_with(
            name=name,
            domaincontroller=domaincontroller)
        db.session.add.assert_called()
        # ensure we forwarded the query to the domain controller
        requests.post.assert_called_with(
            "http://test",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'},
            data=dumps(
                {"name": name,
                 "value": cert_value})
        )

    # TEST to move to nginx-api
    # patch passes mocks from bottom to top
    # def test_post(self, ssl_model, db):
    #     """Send a new certificate"""
    #     print(request.get_json())
    #     cert = "it's a pretty certificate"
    #     request.get_json.return_value = cert
    #     from jeto.services import SSLApi
    #     name = "mycert"
    #     open_mock = mock_open()
    #     with patch('jeto.services.open', open_mock, create=True):
    #         SSLApi().post(name=name)
    #     print(open_mock.mock_calls)
    #     open_mock.assert_called_with()
    #     ssl_model.assert_called_with(name)


if __name__ == '__main__':
    main()
