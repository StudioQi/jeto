#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db


# @TODO Should be named APIKey (without the 's')
class APIKeys(db.Model):
    # @TODO should not have a 's' at the end as well
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    comment = db.Column(db.String(255))
    user_id = db.Column(
        db.String(64),
        db.ForeignKey('user.id')
    )
