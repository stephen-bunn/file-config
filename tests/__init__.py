# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

import sys

from hypothesis import settings, HealthCheck

settings.register_profile(
    "windows", suppress_health_check=[HealthCheck.too_slow], deadline=None
)

if sys.platform in ("win32",):
    settings.load_profile("windows")
