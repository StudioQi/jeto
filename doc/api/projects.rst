.. _projects:

Projects
========

.. _object-project:

Project object
--------------

.. code-block:: javascript
                
                "base_path": <path on the system>, 
                "git_address": <git url>
                "id": <project ID>
                "instances": [ <list of instances related to project>]

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

.. code-block:: javascript

                {
                    "name":"<project name>",
                    "base_path":"",
                    "git_address":"<git url>",
                    "state":"create"}
   



/api/projects/<id>/git-references
---------------------------------

GET
^^^

Returns a list of git references related to the project
