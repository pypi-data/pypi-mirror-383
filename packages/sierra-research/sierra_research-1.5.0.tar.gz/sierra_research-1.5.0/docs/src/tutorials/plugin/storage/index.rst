.. _tutorials/plugin/storage:

=============================
Creating a New Storage Plugin
=============================

For the purposes of this tutorial, I will assume you are creating a new storage
:term:`Plugin` ``infinite``, and the code for that plugin lives in
``$HOME/git/plugins/storage/infinite``.

Before beginning, see the :ref:`plugins/devguide` for a general overview of
creating a new plugin.

To begin, create the following filesystem structure in
``$HOME/git/plugins/infinite``.

-  ``plugin.py`` - This file is required, and is where most of the bits for the
   plugin will go. You don't *have* to call it this; if you want to use a
   different name, see :ref:`plugins/devguide/schemas` for options.

- ``cmdline.py`` This file is optional. If your new plugin doesn't need any
  additional cmdline arguments, you can skip it.

These files will be populated as you go through the rest of the tutorial.

#. Create additional cmdline arguments for the new engine by following
   :ref:`plugins/devguide/cmdline`.

#. Create the following filesystem structure in
   ``$HOME/git/plugins/storage/infinite``:

   .. tabs::

      .. tab::  ``plugin.py``

         .. include:: plugin.rst

#. Put ``$HOME/git/plugins`` on your :envvar:`SIERRA_PLUGIN_PATH`. Then
   your plugin can be selected as ``--storage=storage.infinite``.
