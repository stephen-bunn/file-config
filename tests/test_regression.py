# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

from typing import Dict, List

import pytest
import file_config


def test_issue19():
    @file_config.config
    class Config(object):
        hooks = file_config.var(Dict[str, List[str]])

    file_config.build_schema(Config)
