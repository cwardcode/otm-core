# -*- coding: utf-8 -*-




from django.urls import re_path

from opentreemap.urls import instance_pattern
from stormwater import routes


urlpatterns = [
    re_path(r'%s/polygon-for-point/$' % instance_pattern,
        routes.polygon_for_point, name='polygon_for_point'),
]
