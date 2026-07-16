from django.urls import include, re_path
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView


from .views import (RegistrationView, ActivationView, LoginForm,
                   PasswordResetView)


urlpatterns = [
    re_path(
        r'^login/$',
        LoginView.as_view(authentication_form=LoginForm),
        name='login'
    ),
    re_path(r'^activation-complete/$',
        TemplateView.as_view(template_name='registration/activation_complete.html'),  # NOQA
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get
    # to the view; that way it can return a sensible "invalid key"
    # message instead of a confusing 404.
    re_path(r'^activate/(?P<activation_key>\w+)/$',
        ActivationView.as_view(),
        name='registration_activate'),
    re_path(r'^register/$',
        RegistrationView.as_view(),
        name='registration_register'),
    re_path(r'^register/complete/$',
        TemplateView.as_view(template_name='registration/registration_complete.html'),  # NOQA
        name='registration_complete'),
    re_path(r'^register/closed/$',
        TemplateView.as_view(template_name='registration/registration_closed.html'),  # NOQA
        name='registration_disallowed'),
    re_path(r'password/reset/$', PasswordResetView.as_view(),
        name='auth_password_reset'),
    re_path(r'', include('registration.auth_urls')),
]
