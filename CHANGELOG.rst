=========
Changelog
=========

| All notable changes to this project will be documented in this file.
| The format is based on `Keep a Changelog <http://keepachangelog.com/en/1.0.0/>`_ and this project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.
|

`0.0.8`_ (*2018-10-16*)
-----------------------
- adding ``sort_keys`` support for ``json`` dumpers
- adding conditional ``validate`` boolean flag for ``load_<json,toml,yaml,etc...>`` config method (performs pre-validation of loaded dictionary)
- fixing typecasting of loaded content when var is missing in content, now sets var to None
- improved tests via a hypothesis dynmaic config instance builder
- removing support for `complex <https://docs.python.org/3.8/library/functions.html#complex>`_ vars since no serializers support them

`0.0.7`_ (*2018-10-12*)
----------------------
- adding ``prefer`` keyword to use specific serialization handler
- adding ``inline_tables`` argument for ``toml`` handlers (takes a list of fnmatch patterns)
- adding support for `toml <https://github.com/uiri/toml>`_

`0.0.6`_ (*2018-10-08*)
-----------------------
- fixing ``make_config`` not using any passed in ``file_config.var`` instances
- added ``indent`` dumping argument for ``JSONHandler``
- improved documentation in ``file_config.schema_builder``
- improved sphinx linking from ``getting-started.rst`` to generated autodocs

`0.0.5`_ (*2018-10-05*)
-----------------------
- added better docstrings
- added better documentation in rtd
- fixed ``file_config._file_config._build`` for ``file_config.Regex`` types
- fixed ``file_config.utils.typecast`` for serializing to ``str`` instead of None

`0.0.4`_ (*2018-10-04*)
-----------------------
- added basic sphinx documentation
- fixing dynamic type casting for config var typing types


.. _0.0.8: https://github.com/stephen-bunn/file-config/releases/tag/v0.0.8
.. _0.0.7: https://github.com/stephen-bunn/file-config/releases/tag/v0.0.7
.. _0.0.6: https://github.com/stephen-bunn/file-config/releases/tag/v0.0.6
.. _0.0.5: https://github.com/stephen-bunn/file-config/releases/tag/v0.0.5
.. _0.0.4: https://github.com/stephen-bunn/file-config/releases/tag/v0.0.4
