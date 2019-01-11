=========
Changelog
=========

| All notable changes to this project will be documented in this file.
| The format is based on `Keep a Changelog <http://keepachangelog.com/en/1.0.0/>`_ and this project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_.
|

.. towncrier release notes start

`0.3.4 <https://github.com/stephen-bunn/file-config/releases/tag/v0.3.4>`_ (*2019-01-11*)
=========================================================================================

Bug Fixes
---------

- Fixing typing._GenericAlias typecasting raising AttributeError `#21 <https://github.com/stephen-bunn/file-config/issues/21>`_


`0.3.3 <https://github.com/stephen-bunn/file-config/releases/tag/v0.3.3>`_ (*2019-01-10*)
=========================================================================================

Bug Fixes
---------

- Fixing regex check bug where ``type_.__name__`` raises an ``AttributeError`` on ``typing.List`` edge case `#19 <https://github.com/stephen-bunn/file-config/issues/19>`_
- Fixing ``dump_x`` handlers not using kwargs like ``dumps_x`` handlers `#20 <https://github.com/stephen-bunn/file-config/issues/20>`_


`0.3.2 <https://github.com/stephen-bunn/file-config/releases/tag/v0.3.2>`_ (*2019-01-09*)
=========================================================================================

Bug Fixes
---------

- Fixing schema builder where building schemas for object types with nested typing types silently fails `#18 <https://github.com/stephen-bunn/file-config/issues/18>`_

Documentation
-------------

- Showing newly documented private methods in package documentation 
- Adding basic docstrings for private schema_builder functions 
- Adding basic docstrings for util functions 

Miscellaneous
-------------

- Updating copyright statements from 2018 to 2019 
- Fixing missing wheel in release


`0.3.1 <https://github.com/stephen-bunn/file-config/releases/tag/v0.3.1>`_ (*2018-12-18*)
=========================================================================================

Features
--------

- Adding `defusedxml <https://pypi.org/project/defusedxml/>`_ as fromstring reader in XMLParser `#17 <https://github.com/stephen-bunn/file-config/issues/17>`_

Miscellaneous
-------------

- Fixing lxml required for import


`0.3.0 <https://github.com/stephen-bunn/file-config/releases/tag/v0.3.0>`_ (*2018-12-16*)
=========================================================================================

Features
--------

- Adding basic ini support through ``configparser`` `#10 <https://github.com/stephen-bunn/file-config/issues/10>`_
- Adding basic xml support through ``lxml`` `#12 <https://github.com/stephen-bunn/file-config/issues/12>`_

Documentation
-------------

- Splitting up Sphinx autodocs into separate sections
- Adding Handlers section to documentation

Miscellaneous
-------------

- Adding ``TYPE_MAPPINGS`` to ``utils.py`` as a way of generically representing available types and their translations
- Project Restructure - restructuring project to provide a better development experience
- Updating from MIT to ISC licensing


`0.2.0 <https://github.com/stephen-bunn/file-config/releases/tag/v0.2.0>`_ (*2018-11-07*)
=========================================================================================
- adding serialization and deserialization support for enums

`0.1.0 <https://github.com/stephen-bunn/file-config/releases/tag/v0.1.0>`_ (*2018-10-26*)
=========================================================================================
- adding ``encoder`` and ``decoder`` var kwargs for customizing how a specific var is serialized/deserialized
- adding support for `python-rapidjson <https://pypi.org/project/python-rapidjson/>`_ as json serializer

`0.0.8 <https://github.com/stephen-bunn/file-config/releases/tag/v0.0.8>`_ (*2018-10-16*)
=========================================================================================
- adding ``sort_keys`` support for ``json`` dumpers
- adding conditional ``validate`` boolean flag for ``load_<json,toml,yaml,etc...>`` config method (performs pre-validation of loaded dictionary)
- fixing typecasting of loaded content when var is missing in content, now sets var to None
- improved tests via a hypothesis dynmaic config instance builder
- removing support for `complex <https://docs.python.org/3.8/library/functions.html#complex>`_ vars since no serializers support them

`0.0.7 <https://github.com/stephen-bunn/file-config/releases/tag/v0.0.7>`_ (*2018-10-12*)
=========================================================================================
- adding ``prefer`` keyword to use specific serialization handler
- adding ``inline_tables`` argument for ``toml`` handlers (takes a list of fnmatch patterns)
- adding support for `toml <https://github.com/uiri/toml>`_

`0.0.6 <https://github.com/stephen-bunn/file-config/releases/tag/v0.0.6>`_ (*2018-10-08*)
=========================================================================================
- fixing ``make_config`` not using any passed in ``file_config.var`` instances
- added ``indent`` dumping argument for ``JSONHandler``
- improved documentation in ``file_config.schema_builder``
- improved sphinx linking from ``getting-started.rst`` to generated autodocs

`0.0.5 <https://github.com/stephen-bunn/file-config/releases/tag/v0.0.5>`_ (*2018-10-05*)
=========================================================================================
- added better docstrings
- added better documentation in rtd
- fixed ``file_config._file_config._build`` for ``file_config.Regex`` types
- fixed ``file_config.utils.typecast`` for serializing to ``str`` instead of None

`0.0.4 <https://github.com/stephen-bunn/file-config/releases/tag/v0.0.4>`_ (*2018-10-04*)
=========================================================================================
- added basic sphinx documentation
- fixing dynamic type casting for config var typing types
