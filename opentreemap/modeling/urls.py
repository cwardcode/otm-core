# -*- coding: utf-8 -*-


from django.urls import re_path

from opentreemap.urls import instance_pattern
from modeling.routes import (run_model_view,
                             modeling_view,
                             get_boundaries_at_point_view,
                             plans_view, plan_view)


urlpatterns = [
    re_path(r'%s/modeling/$' % instance_pattern, modeling_view,
            name='model_trees'),
    re_path(r'%s/modeling/plans/$' % instance_pattern, plans_view,
            name='plans'),
    re_path(r'%s/modeling/plans/(?P<plan_id>\d+)/$' % instance_pattern,
            plan_view, name='plan'),
    re_path(r'%s/modeling/boundaries-at-point/$' % instance_pattern,
            get_boundaries_at_point_view, name='boundaries_at_point'),
    re_path(r'%s/modeling/run/$' % instance_pattern, run_model_view,
            name='run_model'),
]
