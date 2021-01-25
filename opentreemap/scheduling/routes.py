# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial

from django_tinsel.decorators import route, render_template, json_api_call
from django_tinsel.utils import decorate as do

import scheduling.views.management as views

from scheduling.views import update_instance_fields_with_validator
from treemap.decorators import (require_http_method, admin_instance_request,
                                return_400_if_validation_errors)

admin_route = lambda **kwargs: admin_instance_request(route(**kwargs))

json_do = partial(do, json_api_call, return_400_if_validation_errors)

management = do(
    require_http_method('GET'),
    views.management_root)


calendars = admin_route(
    GET=do(render_template('scheduling/calendar.html'),
           views.calendar_info),
    PUT=json_do(update_instance_fields_with_validator,
                views.calendar_info_validator)
)

upcoming_events = admin_route(
    GET=do(render_template('scheduling/upcoming_events.html'),
           views.upcoming_events_info),
    PUT=json_do(update_instance_fields_with_validator,
                views.upcoming_events_info_validator)
)
