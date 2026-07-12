



from django.urls import re_path
from geocode.views import geocode_view, get_esri_token_view

urlpatterns = [
    re_path(r'^geocode$', geocode_view, name='geocode'),
    re_path(r'^get-geocode-token$', get_esri_token_view, name='get_geocode_token')
]
