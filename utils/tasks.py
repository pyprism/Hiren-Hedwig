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
from .bunny import encrypt_mail
from django.db import transaction


@shared_task
def gen_fingerprint(username, pubkey):
    """
    Import public gpg key, generate and save gpg fingerprint
    :param username:
    :param pubkey:
    :return:
    """
    gpg = gnupg.GPG(binary='/usr/bin/gpg', homedir='./keys')
    result = gpg.import_keys(pubkey)
    account = Account.objects.get(username=username)
    pgp = Pgpkey.objects.get(user=account)
    pgp.finger_print = result.fingerprints[0]
    pgp.save()


logger = logging.getLogger(__name__)


@shared_task
def send_mail():
    with transaction.atomic():
        mails = Mail.objects.filter(state='Q').select_related('domain').select_for_update().exclude(domain=None)
        for mail in mails:
            if not mail.emotional_attachment:
                hiren = requests.post(
                    "https://api.mailgun.net/v3/" + mail.domain.name + "/messages",
                    auth=("api", mail.domain.key),
                    data={"from": mail.mail_from,
                          "to": [mail.mail_to],
                          "cc": [mail.cc],
                          "bcc": [mail.bcc],
                          "subject": mail.subject,
                          "h:In-Reply-To": mail.in_reply_to,
                          "html": mail.body})
            else:
                attachments = []
                for attachment in Attachment.objects.filter(mail=mail):
                    attachments.append((("attachment", (attachment.file_name,
                                                        open(attachment.file_obj.path, "rb").read()))))
                    hiren = requests.post(
                        "https://api.mailgun.net/v3/" + mail.domain.name + "/messages",
                        auth=("api", mail.domain.key),
                        files=attachments,
                        data={"from": mail.mail_from,
                              "to": [mail.mail_to],
                              "cc": [mail.cc],
                              "bcc": [mail.bcc],
                              "subject": mail.subject,
                              "html": mail.body})
            if hiren.status_code == 200:  # catch and report failed mail
                bunny = hiren.json()
                mail.message_id = bunny['id']
                mail.state = 'S'
                mail.save()
                encrypt_mail(mail.pk)
            else:
                mail.state = 'F'
                mail.save()
                logger.error('Email sending failed!', exc_info=True, extra={
                    'request': hiren.json(),
                })


