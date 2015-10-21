.. _troubleshooting:

Troubleshooting
===============

Jeto depends on a few services and could seem to 'not work' in case some of those don't respond.
Using the developper console (F12) to view network requests can help.

This is based on an install using the `jeto-dev` project

Logs
----
- `/var/log/jeto/*.log`
- `/var/log/nginx-api/*.log`
- `/var/log/htpasswd-api/*.log`
- `/var/log/vagrant-worker/*.log`

Restarting services
------------------

- `service jeto restart` this will start jeto and htpasswd-api
- `restart nginx-api`
- `restart htpasswd-api`
- `pkill -f worker.py && python <path/to/>vagrant-worker/worker.py {low, low, high, high}`


502 error
---------

0. ensure the error is coming from the nginx configured by jeto and not the nginx on your virtual machine
1. check that the domain associated to your machine is correctly set
   try to re-save the domain in order to re-send the information.
2. check that the domain has been modified in `/etc/nginx/vagrant-sites-enabled`
