.. _instances:

Instances
=========

/api/instances
--------------

GET
^^^

Will return all instances your Token has access to.

**Parameters** : None

**Returns** : Array of instances

POST
^^^^

---

/api/instances/<id>
-------------------

GET
^^^

Will return a single instance if your Token has access.

**Parameters** : Integer

**Returns** : A single Instance object with detailed status or a 404 error page.

POST
^^^^

---

.. _object-instance:

Instance object
---------------

============== ============================== ===================================================================================
Field          Type                           Description
============== ============================== ===================================================================================
id             int                            The unique identifier of the instance object.
name           string                         The name given to the instance when creating it.
path           string                         The path where the instance is on the vagrant-worker system.
archive_url    string                         The archive url given at creation time.
git_reference  string                         Can be a branch or a tag of a git repository. Does not include the repository url.
status         Array of :ref:`object-status`  Array of status objects (ip, name and status)
environment    string                         The environment given at creation time.
host           :ref:`object-host`             The complete host object.
jeto_infos     :ref:`object-jeto-infos`       Everything found in the *jeto.json* file.
============== ============================== ===================================================================================

.. _object-status:

Status object
-------------

============== ========================== ============================================================================================
Field          Type                       Description
============== ========================== ============================================================================================
name           string                     The name of the machine (*default* if not provided by Vagrant standard)
ip             string                     The first IP found on the machine
status         string                     The status of the machine returned by Vagrant (running, poweroff, depends on your provider).
============== ========================== ============================================================================================

.. _object-jeto-infos:

Jeto Infos object
-----------------

Every instance can provide a jeto.json file that include arbitrary values to be passed along to all vagrant commands.
This object is a simple Array containing all key-value in the jeto.json file.
