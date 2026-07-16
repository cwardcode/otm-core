#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if 'DJANGO_SETTINGS_MODULE' not in os.environ:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'opentreemap.settings'
        if os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'ci', 'local_settings.py')):
            os.environ['OTM_LOCAL_SETTINGS'] = os.path.join(os.path.dirname(__file__), '..', 'ci', 'local_settings.py')

    try:
        from django.utils import encoding as django_encoding
        import django.core as django_core
    except Exception:
        django_encoding = None
        django_core = None

    # Provide compatibility shims for unmaintained packages like django-tagging
    if django_encoding is not None:
        # Implement proper shims that maintain original behavior
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

    # Some legacy third-party packages may still expect the old django.core.urlresolvers
    # module path. Provide an alias for backward compatibility.
    if django_core is not None and not hasattr(django_core, 'urlresolvers'):
        import django.urls as django_urls
        django_core.urlresolvers = django_urls
        if 'django.core.urlresolvers' not in sys.modules:
            sys.modules['django.core.urlresolvers'] = django_urls

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
