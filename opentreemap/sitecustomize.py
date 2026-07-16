"""Project-local import bootstrapping for PostgreSQL compatibility."""

from __future__ import annotations

import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# django-tagging expects deprecated Django encoding helpers that were
# removed in newer Django releases. Provide compatibility aliases early
# so imports like `from django.utils.encoding import smart_text` keep
# working during startup.
try:
    from django.utils import encoding as django_encoding
except Exception:
    django_encoding = None

if django_encoding is not None:
    if not hasattr(django_encoding, 'smart_text'):
        django_encoding.smart_text = django_encoding.force_str
    if not hasattr(django_encoding, 'smart_str'):
        django_encoding.smart_str = django_encoding.force_str
