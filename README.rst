File Config
===========

.. code-block:: python

   from typing import List
   import file_config

   @file_config.config(title="My Config", description="A simple/sample config")
   class MyConfig(object):

      @file_config.config(title="Config Group", description="A independent nested config")
      class Group(object):
         name = file_config.var(str)
         type = file_config.var(str, default="config")

      name = file_config.var(str, min=1, max=24)
      version = file_config.var(file_config.Regex(r"^v\d+$"))
      groups = file_config.var(List[Group], min=1)


   my_config = MyConfig(
      name="Sample Config",
      version="v12",
      groups=[
         MyConfig.Group(name="Sample Group")
      ]
   )

   my_config.dumps_json()
   # {"name":"Sample Config","version":"v12","groups":[{"name":"Sample Group","type":"config"}]}


Define Configs
--------------

Making config is straight-forward if you are familiar with attrs syntax.
Decorate a class with the ``file_config.config`` decorator and the class is considered to be a config.

.. code-block:: python

   @file_config.config
   class MyConfig(object):
      pass

You can check if a variable is a config type or instance by using the ``file_config.utils.is_config_type`` or ``file_config.utils.is_config`` methods.

.. code-block:: python

   assert file_config.utils.is_config_type(MyConfig)
   assert file_config.utils.is_config(my_config)

There are two optional attributes are available on the ``file_config.config`` method (both used for validation):

- ``title`` - *Defines the title of the object in the resulting jsonschema*
- ``description`` - *Defines the description of the object in the resulting jsonschema*


.. code-block:: python

   @file_config.config(title="My Config", description="A simple/sample config")
   class MyConfig(object):
      pass



Defining Config Vars
--------------------

The real meat of the config class comes from adding attributes to the config through the ``file_config.var`` method.
Again, if you're familiar with attrs syntax, this should be pretty straight-forward.

.. code-block:: python

   @file_config.config(title="My Config", description="A simple/sample config")
   class MyConfig(object):

      name = file_config.var()


Required
~~~~~~~~

If no args are given the the ``var`` method then the config object only expects that the variable is ``required`` when validating.
You can disable the config exepecting the ``var`` to exist by setting ``required = False``...

.. code-block:: python

   name = file_config.var(required=False)

Type
~~~~

You can specify the type of a ``var`` by using either builtin types or *most common* typing types.
This is accepted as either the first argument to the method or as the keyword ``type``.

.. code-block:: python

   name = file_config.var(type=str)
   keywords = file_config.var(type=typing.List[str])

Commonly you need to validate strings against regular expressions.
Since this package is trying to stick as close as possible to Python's typing there is no builtin type to store regular expressions.
To do handle this a special method was created to store regular expressions in a ``typing`` type.

.. code-block:: python

   version = file_config.var(type=file_config.Regex(r"^v\d+$"))

Nested configs are also possible to throw into the ``type`` keyword of the var.
These are serialized into nested objects in the jsonschema.

.. code-block:: python

   @file_config.config
   class GroupContainer(object):

      @file_config.config
      class Group(object):
         name = file_config.var(str)

      name = file_config.var(str)
      parent_group = file_config.var(Group)
      children_groups = file_config.var(typing.List[Group])

-----

Note that types require to be json serializable.
So types that don't dump out to json (like ``typing.Dict[int, str]``) will fail in the ``file_config.build_schema`` step.

.. code-block:: python

   @file_config.config
   class PackageConfig:
      depends = file_config.var(type=typing.Dict[int, str])

>>> file_config.build_schema(PackageConfig)
Traceback (most recent call last):
  File "main.py", line 21, in <module>
    pprint(file_config.build_schema(PackageConfig))
  File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 278, in build_schema
    return _build_config(config_cls, property_path=[])
  File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 261, in _build_config
    var, property_path=property_path
  File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 218, in _build_var
    _build_type(var.type, var, property_path=property_path + [var.name])
  File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 182, in _build_type
    return builder(value, property_path=property_path)
  File "/home/stephen-bunn/Git/file-config/file_config/schema_builder.py", line 160, in _build_object_type
    f"cannot serialize object with key of type {key_type!r}, "
ValueError: cannot serialize object with key of type <class 'int'>, located in var 'depends'

Title
~~~~~

TODO: Document title

Description
~~~~~~~~~~~

TODO: Document description


Serialization / Deserialization
-------------------------------

Be default dictionary, json, and pickle serialization is included.


>>> config_dict = file_config.to_dict(my_config)
OrderedDict([('name', 'Sample Config'), ('version', 'v12'), ('groups', [OrderedDict([('name', 'Sample Group'), ('type', 'config')])])])
>>> new_config = file_config.from_dict(MyConfig, config_dict)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


>>> json_content = my_config.dumps_json()
{"name":"Sample Config","version":"v12","groups":[{"name":"Sample Group","type":"config"}]}
>>> new_config = MyConfig.loads_json(json_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


>>> pickle_content = my_config.dumps_pickle()
b'\x80\x04\x95\x7f\x00\x00\x00\x00\x00\x00\x00\x8c\x0bcollections\x94\x8c\x0bOrderedDict\x94\x93\x94)R\x94(\x8c\x04name\x94\x8c\rSample Config\x94\x8c\x07version\x94\x8c\x03v12\x94\x8c\x06groups\x94]\x94h\x02)R\x94(h\x04\x8c\x0cSample Group\x94\x8c\x04type\x94\x8c\x06config\x94uau.'
>>> new_config = MyConfig.loads_pickle(pickle_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


Serializing yaml requires ``pyyaml``, ``pipenv install file-config[pyyaml]``

>>> yaml_content = my_config.dumps_yaml()
name: Sample Config
version: v12
groups:
- name: Sample Group
  type: config
>>> new_config = MyConfig.loads_yaml(yaml_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


Serializing toml requires ``tomlkit``, ``pipenv install file-config[tomlkit]``


>>> toml_content = my_config.dumps_toml()
name = "Sample Config"
version = "v12"
[[groups]]
name = "Sample Group"
type = "config"
>>> new_config = MyConfig.loads_toml(toml_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


Serializing message pack requires ``msgpack``, ``pipenv install file-config[msgpack]``


>>> msgpack_content = my_config.dumps_msgpack()
b'\x83\xa4name\xadSample Config\xa7version\xa3v12\xa6groups\x91\x82\xa4name\xacSample Group\xa4type\xa6config'
>>> new_config = MyConfig.loads_msgpack(msgpack_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


Validation
----------

Validation is done through jsonschema and can be used to check a config instance using the ``validate`` method.

>>> file_config.validate(my_config)
None
>>> my_config.version = "12"
>>> file_config.validate(mod_config)
Traceback (most recent call last):
  File "main.py", line 61, in <module>
    print(file_config.validate(my_config))
  File "/home/stephen-bunn/Git/file-config/file_config/_file_config.py", line 313, in validate
    to_dict(instance, dict_type=dict), build_schema(instance.__class__)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 823, in validate
    cls(schema, *args, **kwargs).validate(instance)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 299, in validate
    raise error
jsonschema.exceptions.ValidationError: '12' does not match '^v\\d+$'
Failed validating 'pattern' in schema['properties']['version']:
    {'$id': '#/properties/version', 'pattern': '^v\\d+$', 'type': 'string'}
On instance['version']:
    '12'

The attribute types added config vars **do not** imply type checking when creating an instance of the class.
Attribute types are used for generating the jsonschema for the config and validating the model.
This allows you to throw any data you need to throw around in the config class, but validate the config only when you need to.

You can get the jsonschema that is created to validate a config class through the ``build_schema`` method.

>>> file_config.build_schema(ModConfig)
{'$id': 'MyConfig.json',
 '$schema': 'http://json-schema.org/draft-07/schema#',
 'description': 'A simple/sample config',
 'properties': {'groups': {'$id': '#/properties/groups',
                           'items': {'$id': '#/properties/groups/items',
                                     'description': 'A independent nested '
                                                    'config',
                                     'properties': {'name': {'$id': '#/properties/groups/items/properties/name',
                                                             'type': 'string'},
                                                    'type': {'$id': '#/properties/groups/items/properties/type',
                                                             'default': 'config',
                                                             'type': 'string'}},
                                     'required': ['name', 'type'],
                                     'title': 'Config Group',
                                     'type': 'object'},
                           'minItems': 1,
                           'type': 'array'},
                'name': {'$id': '#/properties/name',
                         'maxLength': 24,
                         'minLength': 1,
                         'type': 'string'},
                'version': {'$id': '#/properties/version',
                            'pattern': '^v\\d+$',
                            'type': 'string'}},
 'required': ['name', 'version', 'groups'],
 'title': 'My Config',
 'type': 'object'}

