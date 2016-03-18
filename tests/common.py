#!/usr/bin/env python
import sys
import os
# make ../jeto available as a module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mock import MagicMock, patch, Mock


mmock = Mock()
mock = MagicMock(autospec=True)

attrs = {'__init__': lambda *args, **kwargs: None}
bases = (object,)

restful = MagicMock(autospec=True)
mock_resource = type('Resource', bases, attrs)
restful.Resource = mock_resource

mock_modules = {
    'ansiconv': mock,
    'flask': mock,
    'flask_oauth': mock,
    'flask.ext': mock,
    'flask.ext.login': mock,
    'flask.ext.babel': mock,
    'flask.ext.sqlalchemy': mock,
    'flask.ext.sqlalchemy._compat': mock,
    'flask.signals': mock,
    'flask.ext.principal': mock,
    'flask.ext.restful': restful,
    'logging': mock,
    'redis': mock,
    'requests': mock,
    'rq': mock,
    'slugify': mock,
}

# with patch.dict(
#         'sys.modules',
#         mock_modules):
#     with patch('jeto.db'):
#         from jeto.services import SSLApi
#         # Please PEP8
#         (SSLApi)
