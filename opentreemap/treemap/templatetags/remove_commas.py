from django import template
register = template.Library()

@register.filter
def remove_commas(string):
    return str(string).replace(',', '')