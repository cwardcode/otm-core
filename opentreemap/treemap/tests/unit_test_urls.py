# -*- coding: utf-8 -*-




from django.urls import include, re_path
from django.template import Template, RequestContext
from django.template.response import HttpResponse

from opentreemap import urls


def last_instance(request):
    """
    Returns the PK of the last instance saved in session
    """
    template = Template("{{ last_instance.pk }}")
    return HttpResponse(template.render(RequestContext(request, {})))


urlpatterns = [
    re_path(r'^test-last-instance$', last_instance),
    re_path(r'', include(urls))
]
