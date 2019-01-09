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

   - :mod:`handlers <file_config.handlers>` — *Dumping / Loading handlers for different formats*
   - :mod:`schema_builder <file_config.schema_builder>` — *Config JSONSchema builder*
   - :mod:`utils <file_config.utils>` - *Utilities used within the module*
   - :mod:`contrib <file_config.contrib.xml_parser>` — *Additional utilities that benefit the package*

|
|
|

.. automodule:: file_config._file_config
   :members:
   :undoc-members:
   :show-inheritance:

