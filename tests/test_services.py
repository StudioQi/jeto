#!/usr/bin/env python
from unittest import TestCase
from unittest import main
from mock import patch, mock_open
from common import mock_modules


@patch.dict('sys.modules', mock_modules)
@patch('jeto.db')
@patch('jeto.services.SSL')
class TestSSLApi(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # patch passes mocks from bottom to top
    def test_get(self, ssl_model, db):
        """Get a list of available certificates"""
        # FIXME: find a way to not import at every test (code duplication)
        from jeto.services import SSLApi
        res = SSLApi().get()
        ssl_model.query.all.assert_called_with()
        self.assertEquals(res, ssl_model.query.all())

    @patch('flask.request')
    def test_post(self, request, ssl_model, db):
        """Create a certificate"""
        print(request.get_json)
        from jeto.services import SSLApi
        name = "pretty cert"
        clean_name = "prettycert"
        cert_content = "this is nice"
        request.get_json.return_value = cert_content
        SSLApi().post(name=name)
        ssl_model.assert_called_with(name=clean_name)
        

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
