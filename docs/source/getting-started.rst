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


Defining Configs
================

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
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {},
 'required': [],
 'type': 'object'}

Currently the generated JSONSchema is pretty boring since the ``ProjectConfig`` class is totally empty.
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
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'description': 'The project configuration for my project',
 'properties': {},
 'required': [],
 'title': 'Project Config',
 'type': 'object'}


Config Vars
===========

Now that you have an empty config class, you can start adding variables that should be part of the config.
Adding config vars is simple, but the more constraints you have on your vars the more complex the definition of that var becomes.

You can start off with the most basic config var possible by using the :func:`file_config.var` method.

.. code-block:: python

   @file_config.config
   class ProjectConfig(object):
      name = file_config.var()

By default a config var...

- uses the name you assigned to it in the config class (in this case ``name``)
- is ``required`` for validation

Checkout how the built JSONSchema looks now that you added a basic var.

>>> file_config.build_schema(ProjectConfig)
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {'name': {'$id': '#/properties/name'}},
 'required': ['name'],
 'type': 'object'}


Required
--------

You can make a config var "optional" by setting ``required`` to ``False``.

.. code-block:: python

   @file_config.config
   class ProjectConfig(object):
      name = file_config.var(required=False)

You'll notice that the ``name`` entry in the ``required`` list is now missing from the built JSONSchema.

>>> file_config.build_schema(ProjectConfig)
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {'name': {'$id': '#/properties/name'}},
 'required': [],
 'type': 'object'}


Name
----

You can change the serialization name of the config var by setting ``name`` to some string.
This is useful when you need to use Python keywords as attribute names in the config.

.. code-block:: python

   @file_config.config
   class ProjectConfig(object):
      name = file_config.var()
      type_ = file_config.var(name="type")

>>> file_config.build_schema(ProjectConfig)
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {'name': {'$id': '#/properties/name'},
                'type': {'$id': '#/properties/type'}},
 'required': ['name', 'type'],
 'type': 'object'}

Serialization dumps to/loads from the given ``name`` attribute.

>>> ProjectConfig(name="My Project", type_="config").dumps_json()
'{"name":"My Project","type":"config"}'
>>> ProjectConfig.loads_json('{"name":"My Project","type":"config"}')
ProjectConfig(name='My Project', type_='config')


Type
----

Defining a config var's type is straight forward but can be complex given your config requirements.
A config var's type can either be passed in as the first argument or as the ``type`` kwarg to the :func:`file_config.var` method.

Builtin Types
~~~~~~~~~~~~~

The :func:`file_config.var` can take in any of the `builtin Python types <https://docs.python.org/3/library/stdtypes.html>`_.

.. code-block:: python

   @file_config.config
   class ProjectConfig(object):
      name = file_config.var(str)
      type_ = file_config.var(name="type", type=str)

This results in some extra rules being added to the properties in the built JSONSchema.

>>> file_config.build_schema(ProjectConfig)
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {'name': {'$id': '#/properties/name', 'type': 'string'},
                'type': {'$id': '#/properties/type', 'type': 'string'}},
 'required': ['name', 'type'],
 'type': 'object'}

You'll notice now that both the ``name`` and ``type`` properties have a declared type of ``string``.
So when validating a ``ProjectConfig`` instance where ``type_`` is a string you get no errors...

>>> config = ProjectConfig(name='My Project', type_="config")
>>> print(config)
ProjectConfig(name='My Project', type_="config")
>>> file_config.validate(config)
None

But if validating a ``ProjectConfig`` instance where ``type_`` is an integer, you'll get an error similar to the following...

>>> config.type_ = 0
>>> print(config)
ProjectConfig(name='My Project', type_=0)
>>> file_config.validate(config)
Traceback (most recent call last):
  File "main.py", line 82, in <module>
    file_config.validate(config)
  File "/home/stephen-bunn/Git/file-config/file_config/_file_config.py", line 355, in validate
    to_dict(instance, dict_type=dict), build_schema(instance.__class__)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 861, in validate
    cls(schema, *args, **kwargs).validate(instance)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 305, in validate
    raise error
jsonschema.exceptions.ValidationError: 0 is not of type 'string'
Failed validating 'type' in schema['properties']['type']:
    {'$id': '#/properties/type', 'type': 'string'}
On instance['type']:
    0


Typing Types
~~~~~~~~~~~~

The :func:`file_config.var` can also use :mod:`typing` types as the ``type`` argument.
This allows you to get a bit more specific with the exact format of the var type.

.. code-block:: python

   from typing import Set

   @file_config.config
   class ProjectConfig(object):
      name = file_config.var(str)
      versions = file_config.var(Set[str])

Using a fancy :mod:`typing` type like this will result in the following JSONSchema being built...

>>> file_config.build_schema(ProjectConfig)
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {'name': {'$id': '#/properties/name', 'type': 'string'},
                'versions': {'$id': '#/properties/versions',
                             'items': {'$id': '#/properties/versions/items',
                                       'type': 'string'},
                             'type': 'array'}},
 'required': ['name', 'versions'],
 'type': 'object'}

You might notice that the ``versions`` var says to use :func:`set` as the loaded in type.
However, you can't serialize set out Python sets in many data formats such as JSON, but loading it back into a config instance can cast it back into a set.

>>> ProjectConfig.loads_json('{"name": "Testing", "versions": ["123", "123"]}')
ProjectConfig(name='Testing', versions={'123'})

.. important:: Using :mod:`typing` types requires a bit of intuition. Your defined var type must be JSON serializable.

   .. code-block:: python

      from typing import Dict

      @file_config.config
      class ProjectConfig(object):
         name = file_config.var(str)
         depends = file_config.var(Dict[int, str])

   Trying to build the schema with a non JSON serializable var type (``Dict[int, str]``) will throw an error similar to this...

   >>> file_config.build_schema(ProjectConfig)
   Traceback (most recent call last):
      File "main.py", line 83, in <module>
        file_config.build_schema(ProjectConfig)
      File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 282, in build_schema
        return _build_config(config_cls, property_path=[])
      File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 265, in _build_config
        var, property_path=property_path
      File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 221, in _build_var
        _build_type(var.type, var, property_path=property_path + [var_name])
      File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 182, in _build_type
        return builder(value, property_path=property_path)
      File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 160, in _build_object_type
        f"cannot serialize object with key of type {key_type!r}, "
   ValueError: cannot serialize object with key of type <class 'int'>, located in var 'depends'


Nested Configs
~~~~~~~~~~~~~~

You can also nest configs as types in your config classes.

.. code-block:: python

   from typing import List

   @file_config.config
   class ProjectConfig(object):

      @file_config.config
      class Dependency(object):
         name = file_config.var(str)
         version = file_config.var(str)

   name = file_config.var(str)
   dependencies = file_config.var(List[Dependency])

Building the schema for this config will result in a format you might expect...

>>> file_config.build_schema(ProjectConfig)
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {'dependencies': {'$id': '#/properties/dependencies',
                                 'items': {'$id': '#/properties/dependencies/items',
                                           'properties': {'name': {'$id': '#/properties/dependencies/items/properties/name',
                                                                   'type': 'string'},
                                                          'version': {'$id': '#/properties/dependencies/items/properties/version',
                                                                      'type': 'string'}},
                                           'required': ['name', 'version'],
                                           'type': 'object'},
                                 'type': 'array'},
                'name': {'$id': '#/properties/name', 'type': 'string'}},
 'required': ['name', 'dependencies'],
 'type': 'object'}

Serialization and deserialization of an instance of this config builds instances of the config objects as you would expect...

>>> config = ProjectConfig(
...    name="My Project",
...    dependencies=[ProjectConfig.Dependency(name="A Dependency", version="1.2.3")],
... )
>>> config.dumps_json()
'{"name":"My Project","dependencies":[{"name":"A Dependency","version":"1.2.3"}]}'
>>> ProjectConfig.loads_json('{"name":"My Project","dependencies":[{"name":"A Dependency","version":"1.2.3"}]}')
ProjectConfig(name='My Project', dependencies=[ProjectConfig.Dependency(name='A Dependency', version='1.2.3')])


Regular Expressions
~~~~~~~~~~~~~~~~~~~

In some cases you might need to do string validation based on some regular expression.
Since there is no decent builtin way to specify a pattern as a type you must use the custom :func:`file_config.Regex` method to specify the regular expression to validate against.

.. code-block:: python

   @file_config.config
   class ProjectConfig(object):
      name = file_config.var(str)
      version = file_config.var(file_config.Regex(r"^v\d+$"))

Generating the JSONSchema for this config results in the ``pattern`` property of the ``version`` config var to be populated with the appropriate regular expression.

>>> file_config.build_schema(ProjectConfig)
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {'name': {'$id': '#/properties/name', 'type': 'string'},
                'version': {'$id': '#/properties/version',
                            'pattern': '^v\\d+$',
                            'type': 'string'}},
 'required': ['name', 'version'],
 'type': 'object'}

.. note:: Using the :func:`file_config.Regex` method uses :func:`typing.NewType` to generate a typing instance where the regex you supply is compiled by :func:`re.compile` and stored in the ``__supertype__`` attribute of the newly generated type.

   This method **assumes** that the base type of the attribute is ``string`` (as you cannot do regex matching against any other type).

You can get pretty specific with your config validation by using regular expressions...

.. code-block:: python

   from typing import Dict

   @file_config.config
   class ProjectConfig(object):
      name = file_config.var(str)
      dependencies = file_config.var(Dict[str, file_config.Regex(r"^v\d+$")])


Here is what happens when you try to pass a value into the ``dependencies`` dictionary that doesn't match the provided regular expression...

>>> config = ProjectConfig(name="My Project", dependencies={"A Dependency": "12"})
>>> file_config.validate(config)
Traceback (most recent call last):
  File "main.py", line 88, in <module>
    print(file_config.validate(config))
  File "/home/stephen-bunn/Git/file-config/file_config/_file_config.py", line 363, in validate
    to_dict(instance, dict_type=dict), build_schema(instance.__class__)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 861, in validate
    cls(schema, *args, **kwargs).validate(instance)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 305, in validate
    raise error
jsonschema.exceptions.ValidationError: '12' does not match '^v\\d+$'
Failed validating 'pattern' in schema['properties']['dependencies']['patternProperties']['^(.*)$']:
    {'pattern': '^v\\d+$', 'type': 'string'}
On instance['dependencies']['A Dependency']:
    '12'

.. important:: The generated JSONSchema requires that the regular expression you give must be a full matching pattern (containing ``^`` and ``$`` or ``\A`` and ``\Z``).

   Without start and end terminators in the regular expression JSONSchema will not fully match the string and assume that it is correct.

Extras
------


Validation
==========

You've probably seen some examples of validation in the previous sections (as it relates pretty closely to how to declare config vars).
Validation is done 100% through the use of dynamically generated `JSONSchema <https://json-schema.org/>`_ based on the declarations of the ``config``.

The method used to generate the JSONSchema is :func:`file_config.build_schema`.
You can use this method by simply passing in a class wrapped by :func:`file_config.config`...

For example take the following (pretty specific) config class...

.. code-block:: python

   from typing import List, Dict

   @file_config.config
   class ProjectConfig(object):

      @file_config.config
      class Dependency(object):
         name = file_config.var(str, min=1)
         version = file_config.var(file_config.Regex(r"^v\d+$"))

      name = file_config.var(str, min=1)
      type_ = file_config.var(str, name="type", required=False)
      keywords = file_config.var(List[str], min=0, max=10)
      dependencies = file_config.var(Dict[str, Dependency])


The resulting JSONSchema ends up being the following...

>>> file_config.build_schema(ProjectConfig)
{'$id': 'ProjectConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'properties': {'dependencies': {'$id': '#/properties/dependencies',
                                 'patternProperties': {'^(.*)$': {'$id': '#/properties/dependencies',
                                                                  'properties': {'name': {'$id': '#/properties/dependencies/properties/name',
                                                                                          'minLength': 1,
                                                                                          'type': 'string'},
                                                                                 'version': {'$id': '#/properties/dependencies/properties/version',
                                                                                             'pattern': '^v\\d+$',
                                                                                             'type': 'string'}},
                                                                  'required': ['name',
                                                                               'version'],
                                                                  'type': 'object'}},
                                 'type': 'object'},
                'keywords': {'$id': '#/properties/keywords',
                             'items': {'$id': '#/properties/keywords/items',
                                       'type': 'string'},
                             'maxItems': 10,
                             'minItems': 0,
                             'type': 'array'},
                'name': {'$id': '#/properties/name',
                         'minLength': 1,
                         'type': 'string'},
                'type': {'$id': '#/properties/type', 'type': 'string'}},
 'required': ['name', 'keywords', 'dependencies'],
 'type': 'object'}

Performing validation is very simple.
All you need to do is pass an **instance** of the config into the :func:`file_config.validate` method...

>>> config = ProjectConfig(
...    name="My Project",
...    type_="personal-project",
...    keywords=["example", "test"],
...    dependencies={
...        "a-dependency": ProjectConfig.Dependency(name="A Dependency", version="v12")
...    },
... )
>>> file_config.validate(config)
None

The nice thing about JSONSchema is that it's pretty specific about what exactly is failing when checking an instance that is invalid.
For example, what happens if we give an empty ``name`` in our config instance?

>>> config.name = ""
>>> file_config.validate(config)
Traceback (most recent call last):
  File "main.py", line 108, in <module>
    file_config.validate(config)
  File "/home/stephen-bunn/Git/file-config/file_config/_file_config.py", line 363, in validate
    to_dict(instance, dict_type=dict), build_schema(instance.__class__)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 861, in validate
    cls(schema, *args, **kwargs).validate(instance)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 305, in validate
    raise error
jsonschema.exceptions.ValidationError: '' is too short
Failed validating 'minLength' in schema['properties']['name']:
    {'$id': '#/properties/name', 'minLength': 1, 'type': 'string'}
On instance['name']:
    ''

Pretty explicit right?
Since we use the :mod:`jsonschema` package to perform validation, it provides some really useful information in the exceptions raised from failed validations...

>>> try:
...     file_config.validate(config)
... except jsonschema.exceptions.ValidationError as exc:
...     print(exc.__dict__)
{'cause': None,
 'context': [],
 'instance': '',
 'message': "'' is too short",
 'parent': None,
 'path': deque(['name']),
 'relative_path': deque(['name']),
 'relative_schema_path': deque(['properties', 'name', 'minLength']),
 'schema': {'$id': '#/properties/name', 'minLength': 1, 'type': 'string'},
 'schema_path': deque(['properties', 'name', 'minLength']),
 'validator': 'minLength',
 'validator_value': 1}

This might help you inform your project what to look for to fix in a config.

.. important:: Validation is only applied before loading a new instance from some serialized content or when you explicitly ask it to validate through :func:`file_config.validate`.

   Validation is **not** done as setter methods for :func:`file_config.config` wrapped classes.
   This means you can throw whatever data you want into a config instance and it will never yell at you until you either try to load it from some content or when you explicitly ask for validation to occur.

Dumping / Loading
=================
