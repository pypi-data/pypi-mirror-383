..
   Copyright 2025 John Harwell, All rights reserved.

   SPDX-License-Identifier:  MIT

.. _plugins/proc/imagize:

=========
Imagizing
=========

SIERRA's capabilities for imagizing (translating from :term:`Raw Output Data`
files into images) are detailed in this section. Imagize inputs are treated as
snapshots of 2D or 3D data over time, and after being be turned into image files
in stage 3 they can be rendered into videos in stage 4 (see
:ref:`plugins/prod/render`).

.. _plugins/proc/imagize/req:

Requirements
============

If :term:`Projects <Project>` or :term:`Engines <Engine>` generate files within
the ``main.run_metrics_leaf`` (see :ref:`tutorials/project/config`) directory
for each experimental run which meet the following criteria, then SIERRA can
turn them into images and render them:

- The files reside in a  subdirectory of ``main.run_metrics_leaf``.

- The files have a common stem with a unique numeric ID.

- The stem of all files in the subdir of ``main.run_metrics_leaf`` is the same
  as the subdir name. For example, if the directory name was
  ``foobar/swarm-distribution`` under ``main.run_metrics_leaf`` then all files
  within that directory must be named according to
  ``foobar/swarm-distribution/swarm-distributionXXXXX.<ext>``, where ``XXXXX``
  is any length numeric prefix (possibly preceded by an underscore or dash), and
  ``<ext>`` is any extension supported by the currently selected :ref:`storage
  plugin <plugins/storage>`.

- The name of the subdir of ``main.run_metrics_leaf`` has a corresponding entry
  in ``graphs.yaml``. This is to enable selective imagizing of graphs, so that
  you don't get bogged down if you want to capture imagizing data en masse, but
  only render some of it to videos later. See :ref:`plugins/prod/graphs`
  for details.

.. IMPORTANT::

   Generating the images for each experiment does not happen automatically as
   part of stage 3 because it can take a LONG time and is idempotent. You should
   only pass ``--proc proc.imagize`` the first time you run stage 3 after
   running stage 2.

Usage
=====

This plugin can be selected by adding ``proc.collate`` to the list passed to
``--proc``.

This plugin creates ``<batchroot>/imagize`` when active. All images generated
during stage 3 accrue under this root directory. Each experiment will get their
own subdirectory in this root for their images. E.g.::

  | -- <batchroot>
       |-- imagize
           |-- c1-exp0
           |-- c1-exp1
           |-- c1-exp2
           |-- c1-exp3
           ...



Cmdline Interface
-----------------

.. argparse::
   :filename: ../sierra/plugins/proc/imagize/cmdline.py
   :func: sphinx_cmdline_stage3
   :prog: sierra-cli
