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
from celery import shared_task


@shared_task
def gen_fingerprint(username, pubkey):
    gpg = gnupg.GPG(binary='/usr/bin/gpg', homedir='./keys')
    result = gpg.import_keys(pubkey)
    account = Account.objects.get(username=username)
    pgp = Pgpkey.objects.get(user=account)
    pgp.finger_print = result.fingerprints[0]
    pgp.save()
    print("Done")


