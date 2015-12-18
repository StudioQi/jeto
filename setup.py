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
    packages=['jeto'],
    data_files=[
        ('/opt/jeto/static/css', glob('jeto/static/css/*')),
        ('/opt/jeto/static/lib/select2', glob('jeto/static/lib/select2/*')),
        ('/opt/jeto/static/lib', glob('jeto/static/lib/*.js')),
        ('/opt/jeto/static/lib/jquery', glob('jeto/static/lib/jquery/*')),
        ('/opt/jeto/static/lib/angular', glob('jeto/static/lib/angular/*')),
        ('/opt/jeto/static/lib/bootstrap',
         glob('jeto/static/lib/bootstrap/*')),
        ('/opt/jeto/static/fonts', glob('jeto/static/fonts/*')),
        ('/opt/jeto/static/js', glob('jeto/static/js/*.js')),
        ('/opt/jeto/static/js/controllers',
         glob('jeto/static/js/controllers/*')),
        ('/opt/jeto/static/img', glob('jeto/static/img/*')),
    ]
)
