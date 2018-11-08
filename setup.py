# Copyright (c) 2018 Stephen Bunn (stephen@bunn.io)
# ISC License <https://choosealicense.com/licenses/isc>

import codecs
import pathlib
import configparser

import setuptools

BASE_DIR = pathlib.Path(__file__).parent

config = configparser.ConfigParser()
config.read(BASE_DIR.joinpath("setup.cfg").as_posix())

try:
    metadata = config["metadata"]
except KeyError:
    raise KeyError(f"cannot run setup.py if setup.cfg is missing [metadata] section")

setuptools.setup(
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    package_data={"": ["LICENSE*", "README*"]},
    version=metadata["version"],
)
