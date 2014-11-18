#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    base_path = db.Column(db.String(1024))
    git_address = db.Column(db.String(256))
    instances = db.relationship(
        'VagrantInstance',
        backref='project',
    )

    def __init__(self, id, name, base_path=None, git_address=None, instances=[]):
        self.id = id
        self.name = name
        self.base_path = base_path
        self.git_address = git_address
        self.instances = instances
