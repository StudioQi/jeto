.. _create_new_domain:

Creating a new domain
=====================

Linking a domain to your instance is a quick and easy way to bring your customers to your newly deployed instance.
The domain interface makes some assumptions to bring this devil magic to you:

* You already are the owner of the domain
* The domain already points to the *Domain Controller* (the nginx-api module) of Jeto.

What happens in the background is actually pretty simple:

* You send your information to Jeto
* Jeto sends all the information to your Domain Controller
* Your Domain Controller have nginx installed, creates or edit a new *site* with the information given
* Your Domain Controller reload nginx configuration and the new traffic get sent to the new IP

Let's go back to Jeto and explain all the fields.

.. image:: /images/quickstart/create_new_domain.png

Domain
------

This field contains the primary URL (also known as Domain Name) of your site.
For this exercise, let's call it **www.example.com**.

Aliases
-------

Aliases are domain that should also go to this instance. The most common use is using the same domain with or without the www.
So in our case it will be **example.com**.

Security list
-------------

Also known as htpasswd lists, it helps restricting access to your domain to specific users.
Those lists uses the HTTPDigest authentication protocol and the encryption for the passwords is very very **very** weak.
Still, for development purposes or hiding your pre-production site, it's enough.

You will need a pre-configured htpasswd list. Any users or admins can create a new list from the *Security* tab.

Domain Controllers
------------------

This is where your domain should be pointing. This *Domain Controller* hosts the Jeto module named *nginx-api*. It needs a public and routable IP.
This domain controller will serve as a gateway for all your instance. If unsure, ask your administrator which domain controller to use.

SSL Key
-------

Each domain controller has SSL key defined from the administrator. You can specify if you want to provide SSL support and which key to use. Every key is assigned to a certificate.

Servers
-------

The fun part. Your new vagrant instance has a machine called *web* (it's an example) and it's IP is **10.0.3.110** (it's using the LXC provider). Your application, within this machine is running
at port 8080.

So it the **Servers** section, you will enter in the IP field: 10.0.3.110, in the port field : 8080 and nothing in the SSL port field.

If your application supports it, you can enter a port to SSL and end-to-end encryption will be respected (if you put something in the SSL Key field).
If you put something in the SSL Key field but nothing in the *port SSL* field, SSL encryption will be terminated the Domain Controller.
