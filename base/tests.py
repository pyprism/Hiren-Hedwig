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

    def test_view_returns_correct_template(self):
        response = self.c.get(reverse('login'))
        self.assertTemplateUsed(response, 'base/login.html')

    def test_auth(self):
        respond = self.c.post(reverse('login'), {'username': 'hiren', 'password': 'xyz'})
        self.assertRedirects(respond, reverse('generate_key'))

    def test_redirect_for_unauthenticated_user_works(self):
        response = self.c.get(reverse('inbox'))
        self.assertRedirects(response, '/?next=' + reverse('inbox'))

    def test_redirect_works_for_bad_auth(self):
        respond = self.c.post(reverse('inbox'), {'username': 'hiren', 'password': 'bad pass'})
        self.assertRedirects(respond, '/?next=' + reverse('inbox'))


class SignupViewTest(TestCase):

    def setUp(self):
        self.c = Client()

    def test_signup_url_resolves_to_signup_view(self):
        found = resolve(reverse('signup'))
        self.assertEqual(found.func, views.signup)

    def test_view_returns_correct_template(self):
        response = self.c.get(reverse('signup'))
        self.assertTemplateUsed(response, 'base/signup.html')




