"""Project-local import bootstrapping for PostgreSQL compatibility."""

from __future__ import annotations

import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# Some legacy third-party packages may still expect the old django.core.urlresolvers
# module path. Provide an alias for backward compatibility.
try:
    import django.core as django_core
except Exception:  # pragma: no cover - import may fail before Django is installed
    django_core = None

if django_core is not None:
    if not hasattr(django_core, 'urlresolvers'):
        import django.urls as django_urls
        django_core.urlresolvers = django_urls
    if 'django.core.urlresolvers' not in sys.modules:
        import django.urls as django_urls
        sys.modules['django.core.urlresolvers'] = django_urls
