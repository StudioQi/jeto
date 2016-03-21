#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db
from datetime import datetime

# AuditLog model
# Used to track all actions.
# Is not related to any other DB in case an object is deleted


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer)
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(255))
    object_name = db.Column(db.String(255))
    action = db.Column(db.String(255))
    user_id = db.Column(db.String(64))
    user_name = db.Column(db.String(255))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    summary = db.Column(db.Text)
    request_details = db.Column(db.Text)
    result = db.Column(db.String(255))


def auditlog(
        user,
        action,
        obj,
        object_type=None,
        request_details=None,
        summary=None):
    object_name = getattr(obj, 'name', str(obj))
    object_type = object_type or type(obj).__name__
    if summary is None:
        summary = u"{} executed action {} on {} {}".format(
            user.name,
            action,
            object_type,
            object_name)
    l = AuditLog(
        user_id=user.id,
        user_name=user.name,
        object_id=getattr(obj, 'id', None),
        object_type=object_type,
        request_details=str(request_details),
        object_name=object_name,
        summary=summary)
    db.session.add(l)
    db.session.commit()
