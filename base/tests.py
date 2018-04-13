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
        self.user = Account.objects.create_user(username='hiren', password="xyz")
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

    def test_redirect_for_logged_in_user(self):
        self.c.force_login(self.user)
        response = self.c.get(reverse('login'))
        self.assertRedirects(response, reverse('inbox'))

    def test_initialized_user_redirect(self):
        user = Account.objects.get(username='hiren')
        user.initialized = True
        user.save()
        response = self.c.post(reverse('login'), {'username': 'hiren', 'password': 'xyz'})
        self.assertRedirects(response, reverse('inbox'))

    def test_login_failed(self):
        response = self.c.post(reverse('login'), {'username': 'bad_bunny', 'password': 'xyz'}, follow=True)
        self.assertRedirects(response, reverse('login'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.message, 'Username/Password is not valid!')
        self.assertEqual(message.tags, 'warning')


class SignupViewTest(TestCase):

    def setUp(self):
        self.c = Client()

    def test_signup_url_resolves_to_signup_view(self):
        found = resolve(reverse('signup'))
        self.assertEqual(found.func, views.signup)

    def test_view_returns_correct_template(self):
        response = self.c.get(reverse('signup'))
        self.assertTemplateUsed(response, 'base/signup.html')

    def test_new_account_creation(self):
        self.c.post(reverse('signup'), {'username': 'hiren', 'password': 'xyz'})
        self.assertEqual(Account.objects.count(), 1)

    def test_response_after_account_creation(self):
        response = self.c.post(reverse('signup'), {'username': 'hiren', 'password': 'xyz'}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.message, 'Account created successfully!')
        self.assertEqual(message.tags, 'success')

        self.assertRedirects(response, reverse('login'))

    def test_first_user_is_admin(self):
        self.c.post(reverse('signup'), {'username': 'hiren', 'password': 'xyz'})
        user = Account.objects.get(username='hiren')
        self.assertEqual(user.is_admin, True)

    def test_second_user_is_not_admin(self):
        self.c.post(reverse('signup'), {'username': 'hiren', 'password': 'xyz'})
        self.c.post(reverse('signup'), {'username': 'hiren2', 'password': 'xyz'})
        user = Account.objects.get(username='hiren2')
        self.assertEqual(user.is_admin, False)

    def test_duplicated_username_failed(self):
        Account.objects.create_user(username='hiren', password="xyz")
        response = self.c.post(reverse('signup'), {'username': 'hiren', 'password': 'xyz'}, follow=True)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.message, 'Username is not available!')
        self.assertEqual(message.tags, 'warning')

    def test_redirect_for_logged_in_user(self):
        self.c.force_login(Account.objects.create_user(username='hiren', password="xyz"))
        response = self.c.get(reverse('signup'))
        self.assertRedirects(response, reverse('inbox'))



