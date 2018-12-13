.. raw:: html

   <h1 align="center" style="font-size: 64px;">File Config</h1>
   <p align="center" style="margin: 0px;">
      <a href="https://pypi.org/project/file-config/" target="_blank"><img alt="Supported Versions" src="https://img.shields.io/pypi/pyversions/file-config.svg"></a>
      <a class="badge-align" href="https://www.codacy.com/app/stephen-bunn/file-config?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=stephen-bunn/file-config&amp;utm_campaign=Badge_Grade"><img src="https://api.codacy.com/project/badge/Grade/05b5b7e17d0d471e84b9e32ec50b843a"/></a>
      <a href="https://travis-ci.com/stephen-bunn/file-config" target="_blank"><img alt="Travis CI" src="https://travis-ci.com/stephen-bunn/file-config.svg?branch=master"></a>
      <a href="https://github.com/ambv/black" target="_blank"><img alt="Code Style: Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
   </p>


Easily define configs by creating a :func:`~file_config._file_config.config` decorated class...

.. code-block:: python

   from typing import List, Dict
   import file_config


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


   config = ProjectConfig(
      name="My Project",
      type_="personal-project",
      keywords=["example", "test"],
      dependencies={
          "a-dependency": ProjectConfig.Dependency(name="A Dependency", version="v12")
      },
   )

Configs can be dumped and loaded to various config formats...

>>> json_content = config.dumps_json()
>>> print(json_content)
{"name":"My Project","type":"personal-project","keywords":["example","test"],"dependencies":{"a-dependency":{"name":"A Dependency","version":"v12"}}}
>>> new_config = ProjectConfig.loads_json(json_content)
ProjectConfig(name='My Project', type_='personal-project', keywords=['example', 'test'], dependencies={'a-dependency': ProjectConfig.Dependency(name='A Dependency', version='v12')})
>>> assert new_config == config

and validated...

>>> config.dependencies["a-dependency"].version = "12"
>>> file_config.validate(config)
Traceback (most recent call last):
  File "main.py", line 28, in <module>
    file_config.validate(config)
  File "/home/stephen-bunn/Git/file-config/file_config/_file_config.py", line 373, in validate
    to_dict(instance, dict_type=dict), build_schema(instance.__class__)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 861, in validate
    cls(schema, *args, **kwargs).validate(instance)
  File "/home/stephen-bunn/.local/share/virtualenvs/file-config-zZO-gwXq/lib/python3.6/site-packages/jsonschema/validators.py", line 305, in validate
    raise error
jsonschema.exceptions.ValidationError: '12' does not match '^v\\d+$'
Failed validating 'pattern' in schema['properties']['dependencies']['patternProperties']['^(.*)$']['properties']['version']:
    {'$id': '#/properties/dependencies/properties/version',
     'pattern': '^v\\d+$',
     'type': 'string'}
On instance['dependencies']['a-dependency']['version']:
    '12'


**To get started using this package, please see the** :ref:`getting-started` **page!**

User Documentation
------------------

.. toctree::
   :maxdepth: 2

   getting-started
   handlers
   contributing
   changelog


Project Reference
-----------------

.. toctree::
   :maxdepth: 2

   file_config
