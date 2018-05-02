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


class MailGun(models.Model):
    user = models.ForeignKey('Account', on_delete=models.CASCADE)
    name = models.CharField(max_length=253)
    key = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Pgpkey(models.Model):
    user = models.ForeignKey('Account', on_delete=models.CASCADE)
    public_key = models.TextField()
    private_key = models.TextField()
    finger_print = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Cron(models.Model):
    """
    Cron job tracker
    """
    task_types = (
        ('S', 'Send Mail'),
        ('C', 'Check Mail'),
    )
    task = models.CharField(choices=task_types, max_length=1)
    lock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Setting(models.Model):
    active = models.BooleanField(default=True)
    task_type = (
        ('S', 'Signup'),
    )
    task = models.CharField(choices=task_type, max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



