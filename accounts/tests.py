from django.test import TestCase, tag
from django.urls import reverse


@tag('end_to_end')
class TestLogin(TestCase):
    def test_get_login_page(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
    