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

   file_config.validate(my_config)


Serialization / Deserialization
-------------------------------


>>> config_dict = file_config.to_dict(my_config)
OrderedDict([('name', 'Sample Config'), ('version', 'v12'), ('groups', [OrderedDict([('name', 'Sample Group'), ('type', 'config')])])])
>>> new_config = file_config.from_dict(MyConfig, config_dict)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


>>> json_content = my_config.dumps_json()
{"name":"Sample Config","version":"v12","groups":[{"name":"Sample Group","type":"config"}]}
>>> new_config = MyConfig.loads_json(json_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


>>> yaml_content = my_config.dumps_yaml()
name: Sample Config
version: v12
groups:
- name: Sample Group
  type: config
>>> new_config = MyConfig.loads_yaml(yaml_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


>>> toml_content = my_config.dumps_toml()
name = "Sample Config"
version = "v12"
[[groups]]
name = "Sample Group"
type = "config"
>>> new_config = MyConfig.loads_toml(toml_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


>>> msgpack_content = my_config.dumps_msgpack()
b'\x83\xa4name\xadSample Config\xa7version\xa3v12\xa6groups\x91\x82\xa4name\xacSample Group\xa4type\xa6config'
>>> new_config = MyConfig.loads_msgpack(msgpack_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


>>> pickle_content = my_config.dumps_pickle()
b'\x80\x04\x95\x7f\x00\x00\x00\x00\x00\x00\x00\x8c\x0bcollections\x94\x8c\x0bOrderedDict\x94\x93\x94)R\x94(\x8c\x04name\x94\x8c\rSample Config\x94\x8c\x07version\x94\x8c\x03v12\x94\x8c\x06groups\x94]\x94h\x02)R\x94(h\x04\x8c\x0cSample Group\x94\x8c\x04type\x94\x8c\x06config\x94uau.'
>>> new_config = MyConfig.loads_pickle(pickle_content)
MyConfig(name='Sample Config', version='v12', groups=[MyConfig.Group(name='Sample Group', type='config')])


Validation
----------

>>> file_config.validate(my_config)
None

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
