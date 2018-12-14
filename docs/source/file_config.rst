.. _file_config:

File Config Package
===================

The module that exposes mostly all of the package's functionality.

Although these methods are privatized under the :mod:`~._file_config` namespace they
can be accessed from the imported :mod:`~file_config` module...

.. code-block:: python

   import file_config

   @file_config.config
   class Config(object):
      name = file_config.var(str)

Submodules
----------

   - :mod:`~.handlers` — *Dumping / Loading handlers for different formats*
   - :mod:`~.schema_builder` — *Config JSONSchema builder*
   - :mod:`~.contrib` — *Additional utilities that benefit the package*

|
|
|

.. automodule:: file_config._file_config
   :members:
   :undoc-members:
   :show-inheritance:

