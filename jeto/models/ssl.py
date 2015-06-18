# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db


class SSL(db.Model):
    __tablename__ = 'ssl_keys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    domaincontroller_id = db.Column(
        db.Integer,
        db.ForeignKey('domain_controller.id')
    )
