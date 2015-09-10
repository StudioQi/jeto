.. design-intro:

Intro
=====

The main idea behind Jeto is to deploy full vagrant machines on all environments.
We had two main issues when we begun working on this :

* We could not have a global view of all the vagrant machines installed (global-status didn't exist at the time)
* Having more than one sysadmin meant having a dedicated machine for this.

We then decided to build *Vagrant-Control*, now known as *Jeto*.

The word Ĵeto comes from the esperanto language, which means *release*. `The esperanto language is a constructed language
that aims to be political free and unite all people <https://en.wikipedia.org/wiki/Esperanto>`_.
We saw it fit to use a word in this language.

Ĵeto tries as much as possible to follow the main Unix philosophy : `Do One Thing And It Well <https://en.wikipedia.org/wiki/Unix_philosophy>`_.
For this reason Ĵeto breaks into 4 main modules:

* Ĵeto : the web application providing the nice UI
* nginx-api : python (flask) RESTful application creating/editing nginx sites and reloading nginx.
* htpasswd-api : python (flask) RESTful application creating/editing HTTPDigest password lists.
* vagrant-worker : daemon that runs vagrant commands (up, provision, destroy, etc.) and save results to redis.
  Also takes care of all the file operation (git clone, unarchive package).

.. image:: /images/architecture.png

For a complete description of every modules, see their specific pages:

.. toctree::
    :maxdepth: 1

    /design-architecture/jeto
    /design-architecture/vagrant-worker
    /design-architecture/nginx-api
    /design-architecture/htpasswd-api
    /design-architecture/domain-controllers
