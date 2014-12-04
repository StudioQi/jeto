#!/usr/bin/env python
from unittest import TestCase
from unittest import main
from mock import MagicMock, patch
import sys


mock = MagicMock(autospec=True)
restful = MagicMock(autospec=True)
attrs = {'__init__': lambda *args, **kwargs: None}
bases = (object,)
Hello = type('Resource', bases, attrs)
restful.Resource = Hello
with patch.dict(
        'sys.modules',
        {'logging': mock,
         'rq': mock,
         'ansiconv': mock,
         'slugify': mock,
         'redis': mock,
         'flask': mock,
         'flask_oauth': mock,
         'flask.ext': mock,
         'flask.ext.login': mock,
         'flask.ext.babel': mock,
         'flask.ext.sqlalchemy': mock,
         'flask.ext.principal': mock,
         'flask.ext.restful': restful,
         }
):
    # print(sys.modules)
    # Res = MagicMock(autospec=object)
    from jeto.services import SSLApi


class TestSSLApi(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get(self):
        """Get a list of available certificates"""
        res = SSLApi().get()
        self.assertEquals(res, {'certs': None})


if __name__ == '__main__':
    main()
