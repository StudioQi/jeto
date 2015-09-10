.. _create_new_project:

Creating a new project
======================

Creating a new project is, for now, restricted to Administrators of Jeto.
By clicking on the *Administration* link in the menu, you will find the *Projects* administration page in the sidebar.

.. warning:: Right now Jeto runs the vagrant-worker with root privileges. This is a major security issue if you run Jeto with multi-tenants accounts, but *should be* fine if you run it within your entreprise only with trusted projects. You can find the outstanding issue here : https://github.com/StudioQi/jeto/issues/23


Clicking the **Create a new project** button will bring a nice little popup asking the following information:

Name
----

Can be anything. Will be used by your users when creating a new instance, listing or filtering all the instances.

Git
---

You have the choice between using *Git* or *Direct path*. If using *Git*, enter the git repository URL.
If the project is not public and needs specific ssh keys, it needs to be done manually.
Find the machine running the vagrant-worker (the same machine running Jeto, by default) and put the keys under the *root* account.

Direct path
-----------

If you specify a path here, it will be suggested to the user creating a new instance with this project.
