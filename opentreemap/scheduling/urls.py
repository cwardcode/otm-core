from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from django.conf.urls import url

from scheduling import routes

urlpatterns = [
    url(r'^$', routes.management, name='scheduling'),
    url(r'^calendars/$', routes.calendars, name='calendars'),
    url(r'^upcoming-events/$', routes.upcoming_events, name='upcoming_events'),
]
