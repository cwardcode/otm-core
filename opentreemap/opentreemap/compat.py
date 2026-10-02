from __future__ import annotations

import sys


def apply_django_compat_shims() -> None:
    """Install Django compatibility aliases for unmaintained dependencies."""
    try:
        from django.utils import encoding as django_encoding
    except Exception:
        django_encoding = None

    try:
        from django.utils import http as django_http
    except Exception:
        django_http = None

    try:
        from django.utils import translation as django_translation
    except Exception:
        django_translation = None

    try:
        import django.core as django_core
    except Exception:
        django_core = None

    if all(mod is None for mod in (
            django_encoding, django_http, django_translation, django_core)):
        return

    if django_encoding is not None and not hasattr(django_encoding, 'smart_text'):
        django_encoding.smart_text = django_encoding.smart_str

    if django_encoding is not None and not hasattr(django_encoding, 'force_text'):
        django_encoding.force_text = django_encoding.force_str

    if django_core is not None and not hasattr(django_core, 'urlresolvers'):
        import django.urls as django_urls
        django_core.urlresolvers = django_urls

    if django_core is not None and 'django.core.urlresolvers' not in sys.modules:
        import django.urls as django_urls
        sys.modules['django.core.urlresolvers'] = django_urls

    if django_translation is not None and not hasattr(django_translation, 'ugettext'):
        django_translation.ugettext = django_translation.gettext

    if django_translation is not None and not hasattr(django_translation, 'ugettext_lazy'):
        django_translation.ugettext_lazy = django_translation.gettext_lazy

    if django_translation is not None and not hasattr(django_translation, 'ugettext_noop'):
        django_translation.ugettext_noop = django_translation.gettext_noop

    if django_translation is not None and not hasattr(django_translation, 'ungettext'):
        django_translation.ungettext = django_translation.ngettext

    if django_translation is not None and not hasattr(django_translation, 'ungettext_lazy'):
        django_translation.ungettext_lazy = django_translation.ngettext_lazy

    if django_http is not None and not hasattr(django_http, 'is_safe_url'):
        def _is_safe_url(url, host=None, allowed_hosts=None, require_https=False):
            # Preserve old signature expected by third-party Django<3 code.
            hosts = allowed_hosts
            if hosts is None:
                hosts = {host} if host else set()
            return django_http.url_has_allowed_host_and_scheme(
                url=url,
                allowed_hosts=hosts,
                require_https=require_https,
            )

        django_http.is_safe_url = _is_safe_url
