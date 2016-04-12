from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager


class AccountManager(BaseUserManager):

    def create_user(self, username=None, password=None, **kwargs):
        account = self.model(username=username)

        account.set_password(password)
        account.save()

        return account

    def create_superuser(self, username, password, **kwargs):
        account = self.create_user(username, password, **kwargs)
        account.is_admin = True
        account.save()

        return account


class Account(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    initialized = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    objects = AccountManager()


class Domain(models.Model):
    user = models.ForeignKey('Account', models.CASCADE)
    name = models.CharField(max_length=253)


class DomainSettings(models.Model):
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)
    key = models.CharField(max_length=500)
    incoming = models.BooleanField(default=True)
    auto_delete_message = models.BooleanField(default=False)


class Message(models.Model):
    types = (
        ('incoming', 'Inbox'),
        ('outgoing', 'Sent'),
        ('draft', 'Draft')
    )
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)
    _from = models.EmailField()
    to = models.EmailField(default='')
    subject = models.CharField(max_length=255, default='')
    message = models.TextField(default='')
    message_id = models.CharField(max_length=500)
    cc = models.EmailField(default='')
    bcc = models.EmailField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    type = models.CharField(max_length=5, choices=types)


class ThreadedView(models.Model):
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)
    message = models.ManyToManyField('Message')
    placeholder = models.IntegerField(default=0)


class UrlKey(models.Model):
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)
    mailgun_key = models.CharField(max_length=500)
