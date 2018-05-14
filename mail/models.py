import random
import string
import os
from django.db import models
from base.models import Account, MailGun
from django.utils import timezone
from sortedm2m.fields import SortedManyToManyField


class Contact(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=800, null=True)
    email = models.CharField(max_length=500)
    mail_type = (
        ('F', 'From'),
        ('T', 'To'),
        ('B', 'Blocked'),
    )
    m_type = models.CharField(choices=mail_type, max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Mail(models.Model):
    domain = models.ForeignKey(MailGun, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    mail_from = models.CharField(max_length=500)
    mail_to = models.CharField(max_length=2000)
    cc = models.CharField(max_length=2000, blank=True, null=True)
    bcc = models.CharField(max_length=2000, blank=True, null=True)
    subject = models.CharField(max_length=1000, blank=True, null=True)
    message_id = models.CharField(max_length=500, null=True)  # mailgun message-id
    body = models.TextField()
    mail_state = (
        ('Q', 'Queue'),
        ('S', 'Success'),
        ('D', 'Draft'),
        ('R', 'Received'),
        ('T', 'Trash'),
        ('F', 'Failed'),
    )
    state = models.CharField(choices=mail_state, max_length=1)
    in_reply_to = models.CharField(max_length=500, null=True)  # only used for mail reply
    emotional_attachment = models.BooleanField(default=False)   # lol :P emotional_attachment == mail attachment  :D
    received_datetime = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def create_random_string(length=30):
    if length <= 0:
        length = 30

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join([random.choice(symbols) for x in range(length)])


def upload_to(instance, filename):  # for avoiding file name attacks
    now = timezone.now()
    filename_base, filename_ext = os.path.splitext(filename)
    return 'hiren/attachment/{}_{}{}'.format(
        now.strftime("%Y/%m/%d/%Y%m%d%H%M%S"),
        create_random_string(),
        filename_ext.lower()
    )


class Attachment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    mail = models.ForeignKey(Mail, on_delete=models.CASCADE, null=True)
    file_name = models.CharField(max_length=100)
    file_obj = models.FileField(upload_to=upload_to)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Thread(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    mails = SortedManyToManyField(Mail)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


