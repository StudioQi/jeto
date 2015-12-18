#!/usr/bin/env python

from distutils.core import setup
from glob import glob

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='jeto',
    version='0.5.2',
    description='Release everything !',
    author='Pierre Paul Lefebvre',
    author_email='info@pierre-paul.com',
    install_requires=required,
    url='https://jeto.io',
    packages=[
        'jeto',
        'jeto.models',
        'jeto.services',
    ],
    package_data={
        'jeto': [
            'translations/fr/LC_MESSAGES/*',
            'templates/*.html',
            'templates/*/*.html',
            'templates/*/*/*.html',
            'templates/*/*/*/*.html',
        ]
    },
    data_files=[
        ('bin', ['manage.py']),
        ('static/css', glob('jeto/static/css/*')),
        ('static/lib/select2', glob('jeto/static/lib/select2/*')),
        ('static/lib', glob('jeto/static/lib/*.js')),
        ('static/lib/jquery', glob('jeto/static/lib/jquery/*')),
        ('static/lib/angular', glob('jeto/static/lib/angular/*')),
        ('static/lib/bootstrap',
         glob('jeto/static/lib/bootstrap/*')),
        ('static/fonts', glob('jeto/static/fonts/*')),
        ('static/js', glob('jeto/static/js/*.js')),
        ('static/js/controllers',
         glob('jeto/static/js/controllers/*')),
        ('static/img', glob('jeto/static/img/*')),
        ('migrations', glob('migrations/alembic.ini')),
        ('migrations', glob('migrations/env.py')),
        ('migrations/versions', glob('migrations/versions/*.py')),
    ]
)
