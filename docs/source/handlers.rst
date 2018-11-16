.. _handlers:

========
Handlers
========

Handlers are what provide functionality to serialize to and deserialize from various
file formats. All of the supported file formats should be attribute-value pair data
exchange formats that can be serialized to and from dictionaries.

Whenever a new config instance is created some generic serialization and deserialization
methods are *magically* created based on what handlers are currently available. The
exposed methods are the following:

   - ``config_instance.dump_x(file_object)`` - *dumps an instance to a file object*
   - ``config_instance.dumps_x()`` - *dumps the content to a string*
   - ``ConfigClass.load_x(file_object)`` - *loads an instance from a file object*
   - ``ConfigClass.loads_x(string)`` - *loads an instance from a string*

where ``x`` is the generic name of the handler (e.g. ``json``, ``ini``, ``pickle``,
``toml``, etc...). I will commonly refer to these methods as the
**config serialization methods**.

.. important:: Since handlers such as :class:`~.handlers.JSONHandler`
   have support for multiple serializer libraries, a keyword ``prefer`` is supplied
   to all the config serialization methods. You can use this keyword to indicate what
   library you wish to use for that specific dump or load.

   .. code-block:: python

      # if you have python-rapidjson installed but would prefer to use the builtin json
      config_instance.dumps_json(prefer="json")

   The value of the ``prefer`` keyword is the **module name** not the package name.
   For example `pyyaml <https://pypi.org/project/PyYAML/>`_'s package name is ``pyyaml``
   but it's importable module name is ``yaml``. So you would put ``prefer="yaml"``
   rather than ``prefer="pyyaml"``.


For the following documentation I will be using the following config instance to
showcase the handler's serialization.

.. code-block:: python

   from typing import List, Dict
   from enum import Enum
   import file_config


   class Status(Enum):
      STOPPED = 0
      STARTED = 1


   @file_config.config
   class ProjectConfig(object):

      @file_config.config
      class Dependency(object):
         name = file_config.var(str, min=1)
         version = file_config.var(file_config.Regex(r"^v\d+$"))

      name = file_config.var(str, min=1)
      type_ = file_config.var(str, name="type", required=False)
      keywords = file_config.var(List[str], min=0, max=10)
      status = file_config.var(Status)
      dependencies = file_config.var(Dict[str, Dependency])


   config_instance = ProjectConfig(
      name="My Project",
      type_="personal-project",
      keywords=["example", "test"],
      status=Status.STOPPED,
      dependencies={
         "a-dependency": ProjectConfig.Dependency(name="A Dependency", version="v12")
      },
   )


.. _handlers.json:

JSON
====

`JSON <https://www.json.org/>`_ is probably the most popular, supported, and
straightforward data exchange formats available right now.

Available formatting options for JSON serializers are...

   - ``indent=2`` - *the number of spaces to use for indentation*
   - ``sort_keys=True`` - *sorts keys alphabetically in the resulting json*


.. _handlers.json.json:

:mod:`json`
-----------

Uses the builtin :mod:`json` module for serialization.

.. code-block:: python

   config_instance.dumps_json(prefer="json", indent=2)


.. code-block:: json

   {
      "name": "My Project",
      "type": "personal-project",
      "keywords": [
         "example",
         "test"
      ],
      "status": 0,
      "dependencies": {
         "a-dependency": {
            "name": "A Dependency",
            "version": "v12"
         }
      }
   }


.. _handlers.json.python-rapidjson:

`python-rapidjson <https://pypi.org/project/python-rapidjson/>`_
----------------------------------------------------------------

Compatability with ``python-rapidjson`` requires the installation of it as an extra...

.. code-block:: bash

   pipenv install file-config[python-rapidjson]


Serialization is the same as the default :ref:`handlers.json.json` handler...

.. code-block:: python

   config_instance.dumps_json(prefer="rapidjson", indent=2)

.. code-block:: json

   {
      "name": "My Project",
      "type": "personal-project",
      "keywords": [
         "example",
         "test"
      ],
      "status": 0,
      "dependencies": {
         "a-dependency": {
            "name": "A Dependency",
            "version": "v12"
         }
      }
   }


.. _handlers.json.ujson:

`ujson <https://pypi.org/project/ujson/>`_
------------------------------------------

In my opinion people shouldn't be using ``ujson`` since they don't follow the JSON spec
and are thus incompatible with the default :mod:`json` module for many edge cases.
But I know that lots of packages still depend on it (*for unknown reasons*).

Support for ``ujson`` requires it to be installed as an extra...

.. code-block:: bash

   pipenv install file-config[ujson]

Usage is similar, however notice the resulting json lacks whitespace between key value
pairs (a quirk of ``ujson``).

.. code-block:: python

   config_instance.dumps_json(prefer="ujson", indent=2)

.. code-block:: json

   {
      "name":"My Project",
      "type":"personal-project",
      "keywords":[
         "example",
         "test"
      ],
      "status":0,
      "dependencies":{
         "a-dependency":{
            "name":"A Dependency",
            "version":"v12"
         }
      }
   }



.. _handlers.ini:

INI
===

`INI <https://bit.ly/2DksT5u>`_ is another popular configuration file format. Although
it lacks features available in other file formats people still tend to use it over
better solutions (:ref:`handlers.toml` following a very similar specification).


.. important:: **INI does not support arrays of dictionaries.** Doing so would break
   the specification and be difficult to read. If your resulting dictionary from
   ``file_config.to_dict(config_instance)`` has an array containing dictionaries the
   config serialization methods for ini serialization will raise a :class:`ValueError`.

   If you need to structure your data this way, please switch to using
   :ref:`handlers.toml` as that is one of their key features.


Available formatting options for INI serializers are...

   - ``root="root"`` - *the name of the root section of the resulting ini*
   - ``delimiter=":"`` - *the delimiter to use to indicate nested dictionaries*
   - ``empty_sections=True`` - *allows empty ini sections to exist*


.. _handlers.ini.configparser:

:mod:`configparser`
-------------------

Uses the builtin :mod:`configparser` module for serialization. A custom
:class:`~.contrib.ini_parser.INIParser` is used since the default ``configparser``
module is pretty lackluster.

.. code-block:: python

   config_instance.dumps_ini(prefer="configparser", root="root")

.. code-block:: ini

   [root]
   name = "My Project"
   type = personal-project
   keywords = example
      test
   status = 0

   [root:dependencies:a-dependency]
   name = "A Dependency"
   version = v12



.. _handlers.pickle:

Pickle
======

You really shouldn't ever be serializing and storing things to :mod:`pickle` syntax
since it has pretty serious security flaws with how it is loaded back in. Anyway, here
is how you can do it in ``file_config``.

**There are no format options available for the pickle handler.**


.. _handlers.pickle.pickle:

:mod:`pickle`
-------------

Uses the builtin :mod:`pickle` module for serialization.

.. code-block:: python

   config_instance.dumps_pickle(prefer="pickle")

.. code-block:: bytes

   \x80\x04\x95\xc6\x00\x00\x00\x00\x00\x00\x00\x8c\x0bcollections\x94\x8c\x0bOrderedDict\x94\x93\x94)R\x94(\x8c\x04name\x94\x8c\nMy Project\x94\x8c\x04type\x94\x8c\x10personal-project\x94\x8c\x08keywords\x94]\x94(\x8c\x07example\x94\x8c\x04test\x94e\x8c\x06status\x94K\x00\x8c\x0cdependencies\x94}\x94\x8c\x0ca-dependency\x94h\x02)R\x94(h\x04\x8c\x0cA Dependency\x94\x8c\x07version\x94\x8c\x03v12\x94usu.



.. _handlers.toml:

TOML
====

There are a thousand libraries for parsing `toml <https://github.com/toml-lang/toml>`_
and they are all terrible. Maybe toml is just poorly designed but every single toml
parsing library I've used (in Python) either doesn't fully parse toml correctly or has
some odd quirks that make it hard to work with.

Nevertheless, here are the three best libraries that *currently* exist for parsing toml.

The format options available to toml are the following:

   - ``inline_tables=["dependences.*"]`` - *a glob pattern for inlining tables*


.. _handlers.toml.tomlkit:

`tomlkit <https://pypi.org/project/tomlkit/>`_
----------------------------------------------

Using tomlkit requires it to be installed as an extra...

.. code-block:: bash

   pipenv install file-config[tomlkit]


Usage is just as you might expect...

.. code-block:: python

   config_instance.dumps_toml(prefer="tomlkit", inline_tables=["dependencies.*"])


.. code-block:: toml

   name = "My Project"
   type = "personal-project"
   keywords = ["example", "test"]
   status = 0

   [dependencies]
   a-dependency = {name = "A Dependency",version = "v12"}


.. _handlers.toml.toml:

`toml <https://pypi.org/project/toml/>`_
----------------------------------------

Using toml requires it to be installed as an extra...

.. code-block:: bash

   pipenv install file-config[toml]


Usage is just the same as :ref:`handlers.toml.tomlkit`...

.. code-block:: python

   config_instance.dumps_toml(prefer="toml", inline_tables=["dependencies.*"])

.. code-block:: toml

   name = "My Project"
   type = "personal-project"
   keywords = [ "example", "test",]
   status = 0

   [dependencies]
   a-dependency = { name = "A Dependency", version = "v12" }



.. _handlers.toml.pytoml:

`pytoml <https://pypi.org/project/pytoml/>`_
--------------------------------------------

Using pytoml requires it to be installed as an extra...

.. code-block:: bash

   pipenv install file-config[pytoml]


Pytoml does not support serializing inline tables in any easy manner. So the
``inline_tables`` keyword won't be applied when dumping with `pytoml`_.

.. code-block:: python

   config_instance.dumps_toml(prefer="pytoml")

.. code-block:: toml

   name = "My Project"
   type = "personal-project"
   keywords = ["example", "test"]
   status = 0

   [dependencies]

   [dependencies.a-dependency]
   name = "A Dependency"
   version = "v12"


.. _handlers.yaml:

YAML
====

`Yaml <http://yaml.org/spec/1.2/spec.html>`_ is a data exchange langauge used by many
projects (Docker, TravisCI, etc...) for simple configuration files.

**There are no format options for yaml serialization.**


.. _handlers.yaml.pyyaml:

`pyyaml (yaml) <https://pypi.org/project/PyYAML/>`_
---------------------------------------------------

Using pyyaml requires it to be installed as an extra...

.. code-block:: bash

   pipenv install file-config[pyyaml]


Usage is straightforward...

.. code-block:: python

   config_instance.dumps_yaml(prefer="yaml")


.. code-block:: yaml

   name: My Project
   type: personal-project
   keywords: [example, test]
   status: 0
   dependencies:
   a-dependency:
      name: A Dependency
      version: v12


.. _handlers.message-pack:

Message Pack
============

`MessagePack <https://msgpack.org/index.html>`_ is a byte sized json format which
retains the same structure as json. It's valuable for quick and fast json streams over
network protocols.

**There are no format options for msgpack.**

.. _handlers.message-pack.msgpack:

`msgpack <https://pypi.org/project/msgpack/>`_
----------------------------------------------

Using msgpack requires it to be installed as an extra...

.. code-block:: bash

   pipenv install file-config[msgpack]


Usage is just as you would expect...

.. code-block:: python

   config_instance.dumps_msgpack(prefer="msgpack")

.. code-block:: bytes

   \x85\xa4name\xaaMy Project\xa4type\xb0personal-project\xa8keywords\x92\xa7example\xa4test\xa6status\x00\xacdependencies\x81\xaca-dependency\x82\xa4name\xacA Dependency\xa7version\xa3v12


.. _handlers.xml:

XML
===

`XML <https://www.w3.org/TR/xml/>`_ is an older data exchange format that follows a
nested tag-attribute type structure. A custom :class:`~.contrib.xml_parser.XMLParser` is
used since the many dictionary to xml helper packages out there are not reflective.

The format options available to xml are the following:

   - ``root="root"`` - *the name of the root element in the resulting xml*
   - ``pretty=True`` - *indicates that the resulting xml should be pretty formatted*
   - ``xml_declaration=True`` - *indicates that the xml header should be added*
   - ``encoding="utf-8"`` - *the encoding to use for the resulting xml document*


.. _handlers.xml.lxml:

`lxml <https://pypi.org/project/lxml/>`_
----------------------------------------

Using XML requires ``lxml`` to be installed as an extra...

.. code-block:: bash

   pipenv install file-config[lxml]

Usage is straightforward...

.. code-block:: python

   config_instance.dumps_xml(prefer="lxml", pretty=True, xml_declaration=True)

.. code-block:: xml

   <?xml version='1.0' encoding='UTF-8'?>
   <ProjectConfig>
      <name type="str">My Project</name>
      <type type="str">personal-project</type>
      <keywords>
         <keywords type="str">example</keywords>
         <keywords type="str">test</keywords>
      </keywords>
      <status type="int">0</status>
      <dependencies>
         <a-dependency>
            <name type="str">A Dependency</name>
            <version type="str">v12</version>
         </a-dependency>
      </dependencies>
   </ProjectConfig>
