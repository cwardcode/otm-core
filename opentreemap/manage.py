#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if 'DJANGO_SETTINGS_MODULE' not in os.environ:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'opentreemap.settings'
        if os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'ci', 'local_settings.py')):
            os.environ['OTM_LOCAL_SETTINGS'] = os.path.join(os.path.dirname(__file__), '..', 'ci', 'local_settings.py')

    try:
        import django.core as django_core
    except Exception:
        django_core = None

    # Some legacy third-party packages may still expect the old django.core.urlresolvers
    # module path. Provide an alias for backward compatibility.
    if django_core is not None and not hasattr(django_core, 'urlresolvers'):
        import django.urls as django_urls
        django_core.urlresolvers = django_urls
        if 'django.core.urlresolvers' not in sys.modules:
            sys.modules['django.core.urlresolvers'] = django_urls

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
