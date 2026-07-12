



from django.urls import re_path

from exporter.views import begin_export_endpoint, check_export_endpoint

urlpatterns = [
    re_path(r'(?P<model>(tree|species))/$',
        begin_export_endpoint, name='begin_export'),
    re_path(r'check/(?P<job_id>\d+)/$',
        check_export_endpoint, name='check_export'),
]
