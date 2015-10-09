.. _upgrading:

Manual procedure to upgrade
===========================


1. for each part of jeto (htpasswd-api, nginx-api, vagrant-worker, jeto), update the code.
   beware, a git pull might override custom configuration (ex: jeto path in `vagrant-worker/config.py`)

.. code-block:: bash
                cd <path to>/[htpasswd-api,nginx-api,vagrant-worker,jeto]/
                git pull
                git checkout <desired branch or tag>

2. backup jeto's DB `mysqldump jeto|gzip > jeto-<DATE>.sql.gz`
3. upgrade jeto's DB

.. code-block:: bash
                cd <path to>/jeto
                python manage.py db upgrade
   
4. restart the services
.. code-block:: bash
                pkill -f worker.py
                <path to>/vagrant-worker/worker.py low&
                <path to>/vagrant-worker/worker.py high&
                restart nginx-api
                service restart htpasswd-api restart
                service jeto restart
   
