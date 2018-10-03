.. _getting-started:

===============
Getting Started
===============

| **Welcome to File Config!**
| This page should hopefully provide you with enough information to get you started defining, serializing, and validating config instances.

Installation and Setup
======================

Installing the package should be super duper simple as we utilize Python's setuptools.

.. code-block:: bash

   $ pipenv install file-config
   $ # or if you're old school...
   $ pip install file-config

Or you can build and install the package from the git repo.

.. code-block:: bash

   $ git clone https://github.com/stephen-bunn/file-config.git
   $ cd ./file-config
   $ python setup.py install


Usage
=====

Defining Configs
----------------

Similar to `attrs <https://attrs.readthedocs.io/en/stable/examples.html#basics>`_, the most basic way to setup a new config is to use the :func:`file_config.config` decorator.

.. code-block:: python

   @file_config.config
   class ProjectConfig(object):
      pass


Creating an empty instance of a config class follows the same comparison rules as `attrs <https://attrs.readthedocs.io/en/stable/examples.html#basics>`_.

>>> ProjectConfig()
ProjectConfig()
>>> ProjectConfig() == ProjectConfig()
True
>>> ProjectConfig() is ProjectConfig()
False

One of main features that :mod:`file_config` provides is the ability to generate a `JSONSchema <https://json-schema.org/>`_ dictionary to use for validating the state of a config instance.
You can get the schema by passing a config class to the :func:`file_config.build_schema` method.

>>> file_config.build_schema(ProjectConfig)
{'$id': 'PackageConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {},
 'required': [],
 'type': 'object'}

Currently the generated JSONSchema is pretty boring since the ``PackageConfig`` class is totally empty.
We can add a quick title and description to the root JSONSchema object by adding two arguments to the :func:`file_config.config` decorator...

- ``title`` - *Defines the title of the object in the generated JSONSchema*
- ``description`` - *Defines the description of the object in the generated JSONSchema*

.. code-block:: python

   @file_config.config(
      title="Project Config",
      description="The project configuration for my project"
   )
   class ProjectConfig(object):
      pass


After building the schema again you can see the added ``title`` and ``description`` properties in the resulting JSONSchema dictionary.

>>> file_config.build_schema(ProjectConfig)
{'$id': 'PackageConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'description': 'The project configuration for my project',
 'properties': {},
 'required': [],
 'title': 'Project Config',
 'type': 'object'}


Config Vars
-----------

Now that you have an empty config class, you can start adding variables that should be part of the config.
Adding config vars is simple, but the more constraints you have on your vars the more complex the definition of that var becomes.

You can start off with the most basic config var possible by using the :func:`file_config.var` method.

.. code-block:: python

   @file_config.config(
      title="Project Config",
      description="The project configuration for my project"
   )
   class ProjectConfig(object):

      name = file_config.var()

By default a config var...

- uses the name you assigned to it in the config class (in this case ``name``)
- is required for validation

Checkout how the built JSONSchema looks now that you added a basic var.

>>> file_config.build_schema(ProjectConfig)
{'$id': 'PackageConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'description': 'The project configuration for my project',
 'properties': {'name': {'$id': '#/properties/name'}},
 'required': ['name'],
 'title': 'Project Config',
 'type': 'object'}


Required
~~~~~~~~


Name
~~~~


Type
~~~~


Validation
----------


Serialization
-------------
