# -*- coding: utf-8 -*-


def sanitize_unicode_value(value):
    # Normalize to text for Python 3 csv/json writers.
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return str(value)


# originally copied from, but now divergent from:
# https://github.com/azavea/django-queryset-csv/blob/
# master/djqscsv/djqscsv.py#L123
def sanitize_unicode_record(record):
    obj = type(record)()
    for key, val in record.items():
        obj[sanitize_unicode_value(key)] = sanitize_unicode_value(val)

    return obj
