# -*- coding: utf-8 -*-




from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog

from treemap import routes
from treemap.ecobenefits import within_itree_regions_view
from treemap.instance import URL_NAME_PATTERN
from treemap.urls import USERNAME_PATTERN

from registration_backend.views import RegistrationView


admin.autodiscover()
instance_pattern = r'^(?P<instance_url_name>' + URL_NAME_PATTERN + r')'


# Testing notes:
# We want to test that every URL succeeds (200) or fails with bad data (404).
# If you add/remove/modify a URL, please update the corresponding test(s).
# For URLs included via <app>.urls, see <app>/tests
# For "top level" URLs defined here, see treemap/tests/urls.py (RootUrlTests)

urlpatterns = [
    re_path(r'^robots.txt$', RedirectView.as_view(
        url='/static/robots.txt', permanent=True)),
    # Setting permanent=False in case we want to allow customizing favicons
    # per instance in the future
    re_path(r'^favicon\.png$', RedirectView.as_view(
        url='/static/img/favicon.png', permanent=False)),
    re_path('^comments/', include('django_comments.urls')),
    re_path(r'^', include('geocode.urls')),
    re_path(r'^stormwater/', include('stormwater.urls')),
    re_path(r'^$', routes.landing_page),
    re_path(r'^config/settings.js$', routes.root_settings_js),
    re_path(r'^users/%s/$' % USERNAME_PATTERN,
        routes.user, name='user'),
    re_path(r'^users/%s/edits/$' % USERNAME_PATTERN,
        routes.user_audits, name='user_audits'),
    re_path(r'^users/%s/photo/$' % USERNAME_PATTERN,
        routes.upload_user_photo, name='user_photo'),
    re_path(r'^api/v(?P<version>\d+)/', include('api.urls')),
    # The profile view is handled specially by redirecting to
    # the page of the currently logged in user
    re_path(r'^accounts/profile/$', routes.profile_to_user_page, name='profile'),
    re_path(r'^accounts/logout/$', LogoutView.as_view(next_page='/')),
    re_path(r'^accounts/forgot-username/$', routes.forgot_username,
        name='forgot_username'),
    re_path(r'^accounts/resend-activation-email/$', routes.resend_activation_email,
        name='resend_activation_email'),
    re_path(r'^accounts/', include('registration_backend.urls')),
    # Create a redirect view for setting the session language preference
    # https://docs.djangoproject.com/en/1.0/topics/i18n/#the-set-language-redirect-view  # NOQA
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^not-available$', routes.instance_not_available,
        name='instance_not_available'),
    re_path(r'^unsupported$', routes.unsupported_page, name='unsupported'),
    re_path(r'^main\.css$', routes.compile_scss, name='scss'),
    re_path(r'^eco/benefit/within_itree_regions/$', within_itree_regions_view,
        name='within_itree_regions'),
    re_path(r'^instances/$', routes.instances_geojson),
    re_path(r'^anonymous-boundary/$',
        routes.anonymous_boundary, name='anonymous_boundary'),
    re_path(instance_pattern + r'/accounts/register/$',
        RegistrationView.as_view(),
        name='instance_registration_register'),
    re_path(instance_pattern + r'/', include('treemap.urls')),
    re_path(instance_pattern + r'/importer/', include('importer.urls',
                                                  namespace='importer')),
    re_path(instance_pattern + r'/export/', include('exporter.urls')),
    re_path(instance_pattern + r'/comments/', include('otm_comments.urls')),
    re_path(instance_pattern + r'/management/', include('manage_treemap.urls')),
    re_path(instance_pattern + r'/schedule/', include('schedule.urls')),
    re_path(instance_pattern + r'/scheduling/', include('scheduling.urls')),
    re_path(r'', include('modeling.urls')),
]

if settings.USE_JS_I18N:
    js_i18n_info_dict = {
        'domain': 'djangojs',
        'packages': settings.I18N_APPS,
    }

    urlpatterns = [
        re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(**js_i18n_info_dict))
    ] + urlpatterns

if settings.EXTRA_URLS:
    urlpatterns = [
        re_path(url_pattern, include(url_module))
        for (url_pattern, url_module) in settings.EXTRA_URLS
    ] + urlpatterns

if settings.DEBUG:
    urlpatterns = [re_path(r'^admin/', admin.site.urls)] + urlpatterns

handler404 = 'treemap.routes.error_404_page'
handler500 = 'treemap.routes.error_500_page'
# Not hooked up yet
handler503 = 'treemap.routes.error_503_page'
