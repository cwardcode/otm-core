from django import template
from django.core.files.storage import default_storage


register = template.Library()


register.filter('image_to_url', default_storage.url)
