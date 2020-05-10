from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.urls import reverse

TEST_USER = "test"
TEST_PASSWORD = "Password-1"

User = get_user_model()

@tag('end_to_end')
class LoginEndToEndTestCase(TestCase):
    def setUp(self):
        self.testuser = User.objects.create_user(
            username=TEST_USER, password=TEST_PASSWORD)
    def test_get_login_page(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
    
    def test_login_with_test_user(self):
        response = self.client.login(username=TEST_USER, password=TEST_PASSWORD)
        self.assertEqual(True, response)