from django.core.urlresolvers import reverse

from treemap.tests import make_instance, make_admin_user
from treemap.tests.test_urls import UrlTestCase


class PagesLoadTestCase(UrlTestCase):

    def setUp(self):
        self.instance = make_instance(is_public=True)
        username = make_admin_user(self.instance).username
        self.client.login(username=username, password='password')

    def assert_page_loads(self, django_url_name):
        self.assert_200(self.instance_reverse(django_url_name))

    def assert_page_redirects(self, url_name, expected_url_name):
        self.assert_redirects(self.instance_reverse(url_name),
                              self.instance_reverse(expected_url_name))

    def instance_reverse(self, django_url_name):
        return reverse(django_url_name,
                       kwargs={'instance_url_name': self.instance.url_name})

    def test_management_redirects(self):
        self.assert_page_redirects('scheduling', 'calendars')

    def test_pages_load(self):
        self.assert_page_loads('calendars')
        self.assert_page_loads('upcoming_events')
