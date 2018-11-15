.. _file_config:

File Config Package
===================

The module that exposes mostly all of the package's functionality.

Submodules
----------

.. toctree::
   :maxdepth: 2

   file_config.handlers
   file_config.schema_builder
   file_config.contrib


File Config
-----------

Although these methods are privatized under the ``_file_config`` namespace they can be
accessed from the imported ``file_config`` module...

.. code-block:: python

   import file_config

   @file_config.config
   class Config(object):
      name = file_config.var(str)


.. automodule:: file_config._file_config
   :members:
   :undoc-members:
   :show-inheritance:

