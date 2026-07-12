



from django.urls import re_path

from scheduling import routes
from scheduling.views.management import (
    api_create_event,
    api_delete_event,
    api_delete_all_events,
    api_edit_event
)

urlpatterns = [
    re_path(r'^$', routes.management, name='scheduling'),
    re_path(r'^api/api_create_event/$', api_create_event, name='api_create_event'),
    re_path(r'^api/api_edit_event/$', api_edit_event, name='api_edit_event'),
    re_path(r'^api/api_delete_event/$', api_delete_event, name='api_delete_event'),
    re_path(r'^api/api_delete_all_events/$', api_delete_all_events, name='api_delete_all_events'),
    re_path(r'^calendars/$', routes.calendars, name='calendars'),
    re_path(r'^upcoming-events/$', routes.upcoming_events, name='upcoming_events'),

]
