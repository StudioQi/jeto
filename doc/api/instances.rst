.. _instances:

Instances
=========


/api/instances
--------------

GET
^^^

Will return all instances your Token has access to.

**Parameters** : None

**Returns** : Array of instances :ref:`object-instance`


POST
^^^^

Creates an instance.
Returns : an instance object
Parameters posted as JSON:


====================  =======  ===========
Field                 Type     Description
====================  =======  ===========
name                  string   Name to give the instance
path or gitReference  string   path on the vagrant-worker or git reference
environment           string   what environment to assign the instance
host                  int      ID of the host to create the instance on
state                 string   "create"
async                 bool     Is it an async call ?
====================  =======  ===========



/api/instances/<id>
-------------------

GET
^^^

Will return a single instance if your Token has access.

**Parameters** : Integer, instance ID

**Returns** : A single Instance object with detailed status or a 404 error page.


DELETE
^^^^^^

Delete the specified instance

/api/instances/<id>/commands
-------------------

GET
^^^
returns a list of command IDs ordered from recent to old.

POST
^^^^

Run the actions on the specific instance.

Parameters posted as JSON:

====================  =======  ========
Field                 Type     Values  
====================  =======  ========
action                 string   start,stop,status,runScript,reload,rsync
machine               string   specific machine name to run the action on
====================  =======  ========

rsync
*****

Run `vagrant rsync` (will fail if it is not supported by the provider)

`machine` is optional.
ex: `{"action":"rsync","machine":"www"}`

runScript
*********

This will execute the `script` defined in `jeto.json`. `machine` is mandatory.

ex: `{"action":"runScript","machine":"www","script":"status"}`

/api/instances/<id>/commands/<command id>
-----------------------------------------

GET
^^^
returns the state of the command

Returned objects
----------------

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
project        :ref:`object-project`         The project linked to
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
