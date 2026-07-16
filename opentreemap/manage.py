#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "opentreemap.settings")

    try:
        from django.utils import encoding as django_encoding
    except Exception:
        django_encoding = None

    if django_encoding is not None:
        if not hasattr(django_encoding, 'smart_text'):
            django_encoding.smart_text = django_encoding.force_str
        if not hasattr(django_encoding, 'smart_str'):
            django_encoding.smart_str = django_encoding.force_str

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
