#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from vagrantControl import db


class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    params = db.Column(db.Text)
    provider = db.Column(db.String(128))
    instances = db.relationship(
        'VagrantInstance',
        backref='host',
    )

    def __init__(self, id, name, params, provider):
        self.id = id
        self.name = name
        self.params = params
        self.provider = provider
