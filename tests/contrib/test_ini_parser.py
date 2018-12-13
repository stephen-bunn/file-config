# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import io
import configparser

from hypothesis import given
from hypothesis.strategies import text, characters, integers, floats

import file_config
from file_config.contrib.ini_parser import INIParser
from ..strategies import config


# TODO: expand list of ini safe strategies
INI_SAFE_STRATEGIES = [
    text(characters(blacklist_categories=("Cc", "Cs"))).map(
        lambda x: x.replace("%", "%%")
    ),
    integers(),
    floats(),
]


@given(config(allowed_strategies=INI_SAFE_STRATEGIES))
def test_from_dict(config):
    config_dict = file_config.to_dict(config())
    parser = INIParser.from_dict(config_dict)
    assert isinstance(parser, INIParser)


@given(config(allowed_strategies=INI_SAFE_STRATEGIES))
def test_to_dict(config):
    config_dict = file_config.to_dict(config())
    parser = INIParser.from_dict(config_dict)
    result = parser.to_dict()
    assert isinstance(result, dict)


@given(config(allowed_strategies=INI_SAFE_STRATEGIES))
def test_to_ini(config):
    parser = INIParser.from_dict(file_config.to_dict(config()))
    ini = io.StringIO(parser.to_ini())
    cfg_parser = configparser.ConfigParser()
    cfg_parser.read_file(ini)
    assert isinstance(cfg_parser, configparser.ConfigParser)


@given(config(allowed_strategies=INI_SAFE_STRATEGIES))
def test_from_ini(config):
    ini = INIParser.from_dict(file_config.to_dict(config())).to_ini()
    parser = INIParser.from_ini(ini)
    assert isinstance(parser, INIParser)

