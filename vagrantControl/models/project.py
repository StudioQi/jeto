#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from vagrantControl import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    instances = db.relationship(
        'VagrantInstance',
        backref='project',
    )

    def __init__(self, id, name, instances=[]):
        self.id = id
        self.name = name
        self.instances = instances
