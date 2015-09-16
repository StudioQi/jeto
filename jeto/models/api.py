#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db


class APIKey(db.Model):
    __tablename__ = 'api_key'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    comment = db.Column(db.String(255))
    user_id = db.Column(
        db.String(64),
        db.ForeignKey('user.id')
    )
