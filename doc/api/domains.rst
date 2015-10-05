.. _api-domains:

Domains
=======

/api/domains
------------

GET
^^^

Get a list of all the domains


POST
^^^^

Create a new domain

/api/domains/<id>
-----------------

.. _object-domain:

Domain object
-------------

==================   ====================================  ===========
Attribute            Type                                  Description
==================   ====================================  ===========
aliases              List of :ref:`object-domain-alias`
domain_controller    :ref:`object-domain-controller`
htpasswd             string                                name of the htpasswd to use
id                   int                                   Domain ID
slug                 string                                slug
ssl_key              string                                name of the SSL key to use
upstreams            List of :ref:`object-upstreams`
uri                  string                                Main uri
==================   ====================================  ===========

.. _object-domain-alias:

Domain alias object
-------------------

==================   ====================================  ===========
Attribute            Type                                  Description
==================   ====================================  ===========
id                   int                                   Domain alias ID
uri                  string                                Alias uri
==================   ====================================  ===========

.. _object-upstreams:

Domain upstream object
----------------------

==================   ====================================  ===========
Attribute            Type                                  Description
==================   ====================================  ===========
id                   int                                   Upstream ID
ip                   string                                Backend IP address
port                 string                                HTTP port
port_ssl             string                                HTTPS port
state                string                                'up' 'down' or 'backup'
