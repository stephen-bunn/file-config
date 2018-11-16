# Copyright (c) 2018 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import file_config

FIRST_LEVEL_IMPORTS = (
    "__version__",
    "config",
    "var",
    "validate",
    "to_dict",
    "from_dict",
    "build_schema",
    "make_config",
    "Regex",
    "CONFIG_KEY",
    "handlers",
    "contrib",
)


def test_signature():
    for importable in FIRST_LEVEL_IMPORTS:
        assert hasattr(file_config, importable)
