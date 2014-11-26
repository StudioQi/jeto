# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db


class DomainController(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    address = db.Column(db.String(256))
    port = db.Column(db.String(4))
    accept_self_signed = db.Column(db.Boolean())
    domains = db.relationship(
        'Domain',
        backref=db.backref('domain_controller', lazy='joined'),
    )

    def __init__(self, id, name, address, port, accept_self_signed=False,
                 domains=[]):
        self.id = id
        self.name = name
        self.address = address
        self.port = port
        self.accept_self_signed = accept_self_signed
        self.domains = domains

    def __eq__(self, other):
        if other.id == self.id:
            return True

        return False
