from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import url

from scheduling import routes
from scheduling.views.management import (
    api_create_event,
    api_delete_event,
    api_edit_event
)

urlpatterns = [
    url(r'^$', routes.management, name='scheduling'),
    url(r'^api/api_create_event/$', api_create_event, name='api_create_event'),
    url(r'^api/api_edit_event/$', api_edit_event, name='api_edit_event'),
    url(r'^api/api_delete_event/$', api_delete_event, name='api_delete_event'),
    url(r'^calendars/$', routes.calendars, name='calendars'),
    url(r'^upcoming-events/$', routes.upcoming_events, name='upcoming_events'),

]
