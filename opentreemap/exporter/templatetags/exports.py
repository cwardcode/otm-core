from exporter.lib import export_enabled_for as _export_enabled_for
from django import template

register = template.Library()


@register.filter
def export_enabled_for(instance, user):
    return _export_enabled_for(instance, user)
