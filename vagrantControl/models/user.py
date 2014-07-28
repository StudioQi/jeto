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
    role = db.Column(db.String(32), default=ROLE_DEV)
    last_login = db.Column(db.DateTime)

    def __unicode__(self):
        return 'User {} : {}, Role :{}'.format(
            self.id,
            self.name,
            self.role
        )

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

    def is_admin(self):
        if self.role == ROLE_ADMIN:
            return True
        return False
