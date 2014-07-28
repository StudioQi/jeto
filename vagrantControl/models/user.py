# -=- encoding: utf-8 -=-

from vagrantControl import db

ROLE_DEV = 'dev'
ROLE_ADMIN = 'admin'


class User(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(128), unique=True)
    given_name = db.Column(db.String(128))
    family_name = db.Column(db.String(128))
    picture = db.Column(db.String(256))
    role = db.Column(db.SmallInteger, default=ROLE_DEV)

    def __unicode__(self):
        return 'User {} : {}'.format(self.id, self.name)

    def __str__(self):
        return self.__unicode__()

    def get_id(self):
        return unicode(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True
