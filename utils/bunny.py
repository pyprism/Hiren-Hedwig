import requests
import django
import os
import gnupg
import logging
from datetime import datetime, timedelta
from email.utils import parsedate_tz
import tempfile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hiren.settings")
django.setup()

from base.models import MailGun, Cron, Pgpkey, Account
from mail.models import Mail, Attachment, Thread
from django.core import files
from django.core.exceptions import ObjectDoesNotExist


def to_datetime(datestring):
    """
    convert rfc 2822 datetime format to django supported format
    :param datestring:
    :return:
    """
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])


def encrypt_mail(pk):
    """
    Encrypt mail content after sending
    :param pk:
    :return:
    """
    mail = Mail.objects.select_related('user').get(pk=pk)
    gpg = gnupg.GPG(binary='/usr/bin/gpg', homedir='./keys')
    key = Pgpkey.objects.get(user=mail.user)
    subject = gpg.encrypt(mail.subject, key.finger_print)
    body = gpg.encrypt(mail.body, key.finger_print)
    mail.subject = subject
    mail.body = body
    mail.save()


