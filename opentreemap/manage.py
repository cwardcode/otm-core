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
        import django.core as django_core
    except Exception:
        django_encoding = None
        django_translation = None
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

        if not hasattr(django_encoding, 'python_2_unicode_compatible'):
            def python_2_unicode_compatible(cls):
                return cls

            django_encoding.python_2_unicode_compatible = (
                python_2_unicode_compatible
            )

    # Legacy packages still import removed translation aliases (ugettext*).
    if django_translation is not None:
        if not hasattr(django_translation, 'ugettext'):
            django_translation.ugettext = django_translation.gettext
        if not hasattr(django_translation, 'ugettext_lazy'):
            django_translation.ugettext_lazy = django_translation.gettext_lazy
        if not hasattr(django_translation, 'ungettext'):
            django_translation.ungettext = django_translation.ngettext
        if not hasattr(django_translation, 'ungettext_lazy'):
            django_translation.ungettext_lazy = django_translation.ngettext_lazy

    # Some legacy third-party packages may still expect the old django.core.urlresolvers
    # module path. Provide an alias for backward compatibility.
    if django_core is not None and not hasattr(django_core, 'urlresolvers'):
        import django.urls as django_urls
        django_core.urlresolvers = django_urls
        if 'django.core.urlresolvers' not in sys.modules:
            sys.modules['django.core.urlresolvers'] = django_urls

    try:
        import django.conf.urls as django_conf_urls
        from django.urls import re_path
        if not hasattr(django_conf_urls, 'url'):
            django_conf_urls.url = re_path
    except Exception:
        pass

    try:
        from django.utils import http as django_http
        if not hasattr(django_http, 'is_safe_url'):
            def is_safe_url(url, host=None, allowed_hosts=None, require_https=False):
                if allowed_hosts is None:
                    allowed_hosts = {host} if host else set()
                return django_http.url_has_allowed_host_and_scheme(
                    url=url,
                    allowed_hosts=allowed_hosts,
                    require_https=require_https,
                )

            django_http.is_safe_url = is_safe_url
    except Exception:
        pass

    try:
        import modgrammar
        import modgrammar.util as modgrammar_util
        _orig_word = modgrammar.WORD
        _orig_regularize = modgrammar_util.regularize

        def _word_compat(startchars, restchars=None, *args, **kwargs):
            if isinstance(startchars, bytes):
                startchars = startchars.decode('utf-8')
            if isinstance(restchars, bytes):
                restchars = restchars.decode('utf-8')
            return _orig_word(startchars, restchars, *args, **kwargs)

        def _regularize_compat(grammar):
            if isinstance(grammar, bytes):
                grammar = grammar.decode('utf-8')
            return _orig_regularize(grammar)

        modgrammar.WORD = _word_compat
        modgrammar_util.regularize = _regularize_compat
    except Exception:
        pass

    # django.utils.six was removed; some legacy libs still import it.
    if 'django.utils.six' not in sys.modules:
        import six
        sys.modules['django.utils.six'] = six
        sys.modules['django.utils.six.moves'] = six.moves
        sys.modules['django.utils.six.moves.builtins'] = six.moves.builtins
        sys.modules['django.utils.six.moves.urllib'] = six.moves.urllib
        sys.modules['django.utils.six.moves.urllib.parse'] = six.moves.urllib.parse

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
