"""Project-local import bootstrapping for PostgreSQL compatibility."""

from __future__ import annotations

import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# django-tagging is unmaintained and still imports deprecated Django encoding
# functions. Provide compatibility shims early so imports keep working.
try:
    from django.utils import encoding as django_encoding
    import django.core as django_core
except Exception:  # pragma: no cover - import may fail before Django is installed
    django_encoding = None
    django_core = None

if django_encoding is not None:
    # Implement proper shims for unmaintained packages like django-tagging
    # These maintain the original behavior more faithfully than simple aliasing
    
    if not hasattr(django_encoding, 'smart_text'):
        def smart_text(s, encoding='utf-8', strings_only=False, errors='strict'):
            """
            Return a string representing 's'. Treats bytestrings using the
            specified encoding. If strings_only is True, don't attempt
            conversion of non-string-like objects.
            """
            if isinstance(s, str):
                return s
            if isinstance(s, memoryview):
                return bytes(s).decode(encoding, errors)
            if not isinstance(s, bytes):
                try:
                    if not strings_only:
                        return str(s)
                except Exception:
                    pass
            if isinstance(s, bytes):
                return s.decode(encoding, errors)
            if strings_only:
                return s
            return str(s)
        
        django_encoding.smart_text = smart_text

    if not hasattr(django_encoding, 'smart_str'):
        def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
            """
            Return a string representing 's'. Treats bytestrings using the
            specified encoding. If strings_only is True, don't attempt
            conversion of non-string-like objects.
            """
            if isinstance(s, str):
                return s
            if isinstance(s, memoryview):
                return bytes(s).decode(encoding, errors)
            if not isinstance(s, bytes):
                try:
                    if not strings_only:
                        return str(s)
                except Exception:
                    pass
            if isinstance(s, bytes):
                return s.decode(encoding, errors)
            if strings_only:
                return s
            return str(s)
        
        django_encoding.smart_str = smart_str

    if not hasattr(django_encoding, 'force_text'):
        def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
            """
            Similar to smart_text, except that lazy instances are resolved to
            strings, rather than kept as lazy objects.
            """
            # Resolve lazy objects
            if hasattr(s, '_proxy____args'):
                s = str(s)
            if isinstance(s, str):
                return s
            if isinstance(s, memoryview):
                return bytes(s).decode(encoding, errors)
            if not isinstance(s, bytes):
                try:
                    if not strings_only:
                        return str(s)
                except Exception:
                    pass
            if isinstance(s, bytes):
                return s.decode(encoding, errors)
            if strings_only:
                return s
            return str(s)
        
        django_encoding.force_text = force_text

if django_core is not None:
    if not hasattr(django_core, 'urlresolvers'):
        import django.urls as django_urls
        django_core.urlresolvers = django_urls
    if 'django.core.urlresolvers' not in sys.modules:
        import django.urls as django_urls
        sys.modules['django.core.urlresolvers'] = django_urls
