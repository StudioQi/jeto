#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db


class APIKeys(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    comment = db.Column(db.String)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )
