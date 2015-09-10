.. _api-hosts:

Hosts
=====

/api/hosts
----------


.. _object-host:

Host object
-----------

============== ========================== ===================================================================================
Field          Type                       Description
============== ========================== ===================================================================================
id             int                        Unique identified for the Host.
name           string                     Name given to the host. Used for management purposes.
provider       string                     Provider used on this host. Can be something like *lxc*, *vsphere*, etc.
params         text                       All parameters saved from the admin. Line breaks are replaced by <br>.
============== ========================== ===================================================================================
