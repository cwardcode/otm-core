

# Must run before anything else imports Django/third-party code that relies
# on deprecated encoding helpers (e.g. django-tagging's `smart_text` import).
from .compat import apply_django_compat_shims

apply_django_compat_shims()

from .celery import app as celery_app  # NOQA

__all__ = ['celery_app']
