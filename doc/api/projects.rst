.. _projects:

Projects
========

.. _object-project:

Project object
--------------

===========  ===============================  ===========
Field        Type                             Description
===========  ===============================  ===========
base_path    string                           path on the system 
git_address  string                           git url
id           int                              project ID
instances    Array of :ref:`object-instance`  list of instances related to project
===========  ===============================  ===========

/api/projects
-------------

GET
^^^
Gets a list of projects
Returns :

POST
^^^^

Creates a Projet

Parameters posted as JSON:

========================  ======  ===========
Field                     Type    Description
========================  ======  ===========
base_path or git_address  string  path on the system or git address
name                      string  project name
state                     string  "create"
========================  ======  ===========


/api/projects/<id>/git-references
---------------------------------

**Parameters** : int, project ID

GET
^^^

Returns a list of git references related to the project
