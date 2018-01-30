from django.urls import resolve, reverse
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.test import Client
from . import views
from .models import Account
from freezegun import freeze_time
from django.utils import timezone


class LoginViewTest(TestCase):

    def setUp(self):
        Account.objects.create_user(username='hiren', password="xyz")
        self.c = Client()

    def test_login_url_resolves_to_login_view(self):
        found = resolve(reverse('login'))
        self.assertEqual(found.func, views.login)

    def test_auth(self):
        respond = self.c.post(reverse('login'), {'username': 'hiren', 'password': 'xyz'})
        self.assertRedirects(respond, reverse('inbox'))

    def test_redirect_for_unauthenticated_user_works(self):
        response = self.c.get(reverse('inbox'))
        self.assertRedirects(response, '/?next=' + reverse('inbox'))






