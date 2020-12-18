from django import template

import threading

register = template.Library()

_thread_local = threading.local()

# Some pages contain many tag autocompletes. To avoid re-querying
# we cache the last request and thumbprint. Use thread-local storage
# so each thread can have its own cached value.


@register.filter
def tag_thumbprint(request):
    last_request, last_thumbprint = getattr(_thread_local,
                                            'last_request_and_thumbprint',
                                            (None, None))
    if request == last_request:
        thumbprint = last_thumbprint
    else:
        thumbprint = request.instance.tag_thumbprint
        _thread_local.last_request_and_thumbprint = (request, thumbprint)
    return thumbprint
