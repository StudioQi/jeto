# -*- coding: utf-8 -*-
# vim:fenc=utf-8
from jeto import db

UPSTREAM_STATES = [
    'up',
    'down',
    'backup'
]


class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(255))

    uri = db.Column(db.String(255))
    htpasswd = db.Column(db.String(128))
    ssl_key = db.Column(db.String(128))

    upstreams = db.relationship(
        'Upstream',
        backref='domain',
    )

    domain_controller_id = db.Column(
        db.Integer,
        db.ForeignKey('domain_controller.id')
    )

    aliases = db.relationship(
        'Alias',
        backref=db.backref('domain', lazy='joined'),
    )

    def has_upstream(self, upstream_info):
        for upstream in self.upstreams:
            if upstream == upstream_info:
                return True

        return False

    @property
    def name(self):
        return self.uri

    def __str__(self):
        return 'Domain {}: {} with controller : {}'\
            .format(
                getattr(
                    self, 'id', None),
                self.uri,
                getattr(self.domain_controller, 'id', None))


class Alias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uri = db.Column(db.String(255))
    domain_id = db.Column(
        db.Integer,
        db.ForeignKey('domain.id')
    )


class Upstream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(32))
    port = db.Column(db.Integer)
    port_ssl = db.Column(db.Integer)
    websocket = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(254), default='/')
    state = db.Column(db.Enum(*UPSTREAM_STATES))
    domain_id = db.Column(
        db.Integer,
        db.ForeignKey('domain.id')
    )

    def __eq__(self, other):
        if other.id == self.id:
            return True

        if other.ip == self.ip and other.port == self.port\
                and other.port_ssl == self.port_ssl:
            return True

        return False

    def __str__(self):
        return 'Upstream {}: {} with state : {}'\
            .format(self.id, self.ip, self.state)
