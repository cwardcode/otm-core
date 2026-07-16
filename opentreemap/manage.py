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
        from django.utils import translation as django_translation
        from django.db import models as django_db_models
        import django.core as django_core
    except Exception:
        django_encoding = None
        django_translation = None
        django_db_models = None
        django_core = None

    if django_encoding is not None:
        if not hasattr(django_encoding, 'smart_text'):
            django_encoding.smart_text = django_encoding.force_str
        if not hasattr(django_encoding, 'smart_str'):
            django_encoding.smart_str = django_encoding.force_str
        if not hasattr(django_encoding, 'force_text'):
            django_encoding.force_text = django_encoding.force_str

    if django_translation is not None:
        if not hasattr(django_translation, 'ugettext'):
            django_translation.ugettext = django_translation.gettext
        if not hasattr(django_translation, 'ugettext_lazy'):
            django_translation.ugettext_lazy = django_translation.gettext_lazy
        if not hasattr(django_translation, 'ugettext_noop'):
            django_translation.ugettext_noop = django_translation.gettext_noop

    if django_db_models is not None and not hasattr(django_db_models, 'NullBooleanField'):
        class NullBooleanField(django_db_models.BooleanField):
            def __init__(self, *args, **kwargs):
                kwargs.setdefault('null', True)
                super(NullBooleanField, self).__init__(*args, **kwargs)

        django_db_models.NullBooleanField = NullBooleanField

    if django_core is not None and not hasattr(django_core, 'urlresolvers'):
        import django.urls as django_urls
        django_core.urlresolvers = django_urls
        if 'django.core.urlresolvers' not in sys.modules:
            sys.modules['django.core.urlresolvers'] = django_urls

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
