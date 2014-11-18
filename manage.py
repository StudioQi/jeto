#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
from jeto import app, db
from jeto.models.user import User, ROLE_ADMIN, ROLE_DEV
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def runserver():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)


@manager.command
def add_admin():
    "Grant the admin role to a user"
    users = User.query.all()
    print(
        '\n'.join(
            '{} ) {} {}'.format(idx, user.name, user.email)
            for idx, user in enumerate(users)
        )
    )
    choosenUser = int(raw_input('To which user ? '))
    user = users[choosenUser]
    user.role = ROLE_ADMIN
    db.session.add(user)
    db.session.commit()


@manager.command
def remove_admin():
    "Remove the admin role to a user"
    users = User.query.all()
    print(
        ''.join(
            '{} ) {}'.format(idx, user.name) for idx, user in enumerate(users)
        )
    )
    choosenUser = int(raw_input('To which user ? '))
    user = users[choosenUser]
    user.role = ROLE_DEV
    db.session.add(user)
    db.session.commit()

if __name__ == "__main__":
    manager.run()
