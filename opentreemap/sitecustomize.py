"""Project-local import bootstrapping for PostgreSQL compatibility."""

from __future__ import annotations

import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# django-tagging and older project code expect deprecated Django helpers
# that were removed in newer Django releases. Provide compatibility aliases
# early so imports keep working during startup.
try:
    from django.utils import encoding as django_encoding
    from django.utils import translation as django_translation
    from django.db import models as django_db_models
    from django.urls import reverse as django_reverse
    import django.core as django_core
    from django.contrib.gis.db import models as gis_models
except Exception:  # pragma: no cover - import may fail before Django is installed
    django_encoding = None
    django_translation = None
    django_db_models = None
    django_reverse = None
    django_core = None
    gis_models = None

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

    if gis_models is not None and not hasattr(gis_models, 'NullBooleanField'):
        gis_models.NullBooleanField = NullBooleanField

if gis_models is not None and not hasattr(gis_models, 'GeoManager'):
    gis_models.GeoManager = gis_models.Manager

if django_core is not None:
    if not hasattr(django_core, 'urlresolvers'):
        import django.urls as django_urls
        django_core.urlresolvers = django_urls
    if 'django.core.urlresolvers' not in sys.modules:
        import django.urls as django_urls
        sys.modules['django.core.urlresolvers'] = django_urls
