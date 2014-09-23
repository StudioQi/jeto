# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from vagrantControl import db, app

teams_users = db.Table(
    'teams_users',
    db.Column(
        'team_id',
        db.Integer,
        db.ForeignKey('team.id')
    ),
    db.Column(
        'user_id',
        db.String(128),
        db.ForeignKey('user.id')
    )
)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    users = db.relationship(
        'User',
        secondary=teams_users,
        backref=db.backref('users', lazy='dynamic'),
    )
    permissions_grids = db.relationship(
        'TeamPermissionsGrids',
        backref='team',
    )

    def __init__(self, id, name, users=[]):
        self.id = id
        self.name = name
        self.users = users

    def get_permissions_grids(self):
        return sorted(self.permissions_grids, key=lambda item: item.objectType)
