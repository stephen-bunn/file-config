# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import io

from lxml import etree
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import (
    text,
    lists,
    floats,
    one_of,
    booleans,
    integers,
    characters,
)

import file_config
from file_config.contrib.xml_parser import XMLParser

from ..strategies import config

# TODO: expand list of xml safe strategies
XML_SAFE_STRATEGIES = [
    booleans(),
    text(characters(blacklist_categories=("Cc", "Cs"))),
    integers(),
    floats(),
]
XML_SAFE_STRATEGIES.append(lists(one_of(XML_SAFE_STRATEGIES)))
XML_SAFE_STRATEGIES.append(config(allowed_strategies=XML_SAFE_STRATEGIES))


@given(config(allowed_strategies=XML_SAFE_STRATEGIES))
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_from_dict(config):
    config_dict = file_config.to_dict(config())
    parser = XMLParser.from_dict(config_dict)
    assert isinstance(parser, XMLParser)


@given(config(allowed_strategies=XML_SAFE_STRATEGIES))
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_to_dict(config):
    config_dict = file_config.to_dict(config())
    parser = XMLParser.from_dict(config_dict)
    result = parser.to_dict()
    assert isinstance(result, dict)


@given(config(allowed_strategies=XML_SAFE_STRATEGIES))
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_to_xml(config):
    parser = XMLParser.from_dict(file_config.to_dict(config()))
    xml = parser.to_xml()
    assert isinstance(etree.parse(io.StringIO(xml)), etree._ElementTree)


@given(config(allowed_strategies=XML_SAFE_STRATEGIES))
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_from_xml(config):
    xml = XMLParser.from_dict(file_config.to_dict(config())).to_xml()
    parser = XMLParser.from_xml(xml)
    assert isinstance(parser, XMLParser)
