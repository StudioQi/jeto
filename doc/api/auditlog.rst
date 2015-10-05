.. _auditlog:

AuditLog
========

/api/auditlog
--------

GET
^^^

returns an array of logs
Logs have the following attributes

==============  =======  =============
Attribute       Type     Description
==============  =======  =============
start_date      string   string representation of the time the action was called
summary         string   summary of the action
id              int      auditlog ID
==============  =======  =============

Admin users have the following added details :

===============  =======  =============
Attribute        Type     Description
===============  =======  =============
objectId         int      ID of the acted upon object
objectType       string   ie: domain_controller, team, ...
objectName       string   ie: 'host 1'
request_details  string   the json sent by the client
user_id          string   user ID that called the action
user_name        string   user name that called the action
===============  =======  =============

