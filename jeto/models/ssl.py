# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db


class SSL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
