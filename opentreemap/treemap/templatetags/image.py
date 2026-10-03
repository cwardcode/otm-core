from django import template
from django.core.files.storage import default_storage


register = template.Library()


@register.filter('image_to_url')
def image_to_url(name):
    if not name:
        return ''
    return default_storage.url(name)
