#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import os
from jeto import app, db
from jeto.models.user import User, ROLE_ADMIN, ROLE_DEV
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

manager = Manager(app)
migrate = Migrate(app, db)


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


def _make_context():
    from jeto import app, db
    from jeto.models.domainController import DomainController
    from jeto.models.domain import Domain
    from jeto.models.host import Host
    from jeto.models.project import Project
    from jeto.models.team import Team
    from jeto.models.user import User
    from jeto.models.vagrant import VagrantInstance, VagrantBackend
    return dict(app=app, db=db, DomainController=DomainController,
                Domain=Domain, Host=Host, Project=Project, Team=Team,
                User=User, VagrantInstance=VagrantInstance,
                VagrantBackend=VagrantBackend)

manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=_make_context))

if __name__ == "__main__":
    manager.run()
