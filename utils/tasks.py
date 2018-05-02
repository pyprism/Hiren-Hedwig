import requests
import django
import os
import logging
from datetime import datetime, timedelta
from email.utils import parsedate_tz
import tempfile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hiren.settings")
django.setup()

from base.models import MailGun, Cron, Pgpkey
from mail.models import Mail, Attachment, Thread
from django.core import files
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task


@shared_task
def gen_fingerprint(username, pubkey):
    print("called.........................")


