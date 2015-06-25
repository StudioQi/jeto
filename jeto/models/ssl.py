# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db
from sqlalchemy import UniqueConstraint


class SSL(db.Model):
    __tablename__ = 'ssl_keys'
    __table_args__ = (
        UniqueConstraint('name', 'domaincontroller_id',
                         name='_ssl_dc_uc'),)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    domaincontroller_id = db.Column(
        db.Integer,
        db.ForeignKey('domain_controller.id')
    )
