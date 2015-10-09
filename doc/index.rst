Welcome to Jeto's documentation
===============================


Intro
-----

Jeto gives you a centralized interface to manage hundreds of vagrant machines.
It can interact with multiple providers : Amazon, VMWare, LXC, VirtualBox. Any providers supported by Vagrant is supported by Jeto.

You can create team, add users, projects and hosts and give specific permissions to every team.


.. toctree::
    :maxdepth: 1
    :caption: Quickstart to Jeto

    /quickstart/create-new-instance
    /quickstart/create-new-domain
    /quickstart/create-new-project
    /quickstart/upgrading
    /misc/tips-and-tricks


.. toctree::
    :maxdepth: 1
    :caption: Design and architecture

    /design-architecture/intro
    /design-architecture/jeto
    /design-architecture/vagrant-worker
    /design-architecture/nginx-api
    /design-architecture/htpasswd-api
    /design-architecture/domain-controllers


.. toctree::
    :maxdepth: 1
    :caption: API

    /api/generate-access-token
    /api/endpoints-summary
    /api/instances
    /api/users
    /api/projects
    /api/domains
    /api/htpasswd
    /api/hosts
    /api/ssl
    /api/auditlog
