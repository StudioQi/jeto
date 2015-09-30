.. _tips-and-tricks:

Tips and Tricks
===============

Use jeto.json informations in the provisioning
----------------------------------------------

You can parse the jeto.json file from the Vagrantfile and pass it as needed to the provisionner

.. code-block:: ruby

                require 'json'
                jeto_file = File.read('jeto.json')
                jeto_infos = JSON.parse(jeto_file)
