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
from mail.models import Mail, Attachment, Thread, Contact
from django.core import files
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from .bunny import encrypt_mail, to_datetime
from django.db import transaction
from celery import task


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


@shared_task
def update_contact_list(user_id, to, from_, cc, bcc):
    """
    Add new email in contact list
    :param user_id:
    :param to:
    :param from_:
    :param cc:
    :param bcc:
    :return:
    """
    user = Account.objects.get(pk=user_id)
    Contact.objects.get_or_create(user=user, email=from_, m_type='F')
    if len(to) != 0:
        for i in to.split(','):
            Contact.objects.get_or_create(user=user, email=i, m_type='T')
    if len(cc) != 0:
        for i in cc.split(','):
            Contact.objects.get_or_create(user=user, email=i, m_type='T')
    if len(bcc) != 0:
        for i in bcc.split(','):
            Contact.objects.get_or_create(user=user, email=i, m_type='T')


def items_process(items, mail, encryption):
    """
    Process and save incoming mail
    :param items: API response
    :param mail: db object
    :param encryption: mail's encryption state
    :return:
    """
    for item in items:
        message_id = item['message']['headers']['message-id']
        if not Mail.objects.filter(user=mail.user, message_id=message_id).exists():  # TODO regex domain name
            hiren = requests.get(item['storage']['url'], auth=('api', mail.key))
            if hiren.status_code == 200:
                bunny = hiren.json()
                to = bunny['To']
                if str(to).startswith('<'):
                    cleaned_to = to[1:-1]  # strip <>
                else:
                    cleaned_to = str(to)  # example Someone <exam@xoxo.xyz>
                mail_obj = Mail.objects.create(domain=mail, user=mail.user, mail_from=bunny['From'],
                                               mail_to=cleaned_to, subject=bunny['subject'],
                                               message_id=message_id,
                                               body=bunny['body-html'], state='R', encryption=encryption,
                                               received_datetime=to_datetime(bunny['Date']))
                if bunny['attachments']:  # handle attachment
                    for meow in bunny['attachments']:
                        request = requests.get(meow['url'], stream=True)
                        if request.status_code == requests.codes.ok:
                            tmp = tempfile.NamedTemporaryFile()
                            for block in request.iter_content(1024 * 8):
                                if not block:
                                    break
                                tmp.write(block)
                            Attachment.objects.create(user=mail.user, mail=mail_obj, file_name=meow['name'],
                                                      file_obj=tmp)    # file.Files(tmp)
                            tmp.close()
                    mail_obj.emotional_attachment = True
                    mail_obj.save()
                if encryption:  # encrypt saved mail body
                    encrypt_mail(mail_obj.pk)

                try:  # mail thread.
                    if bunny['In-Reply-To']:  # replied mail
                        reply_id = bunny['In-Reply-To']
                        reply_message_id = reply_id[1:-1]  # stripping <>
                        try:
                            thread = Thread.objects.get(user=mail.user, mails__message_id=reply_message_id)
                            thread.mails.add(mail_obj)
                            thread.read = False
                            thread.save()
                        except ObjectDoesNotExist:  # check if their is a sent mail reply
                            try:
                                sent_mail = Mail.objects.get(user=mail.user, message_id=reply_message_id)
                                new_thread = Thread.objects.create(user=mail.user)
                                new_thread.mails.add(sent_mail, mail_obj)
                            except ObjectDoesNotExist:
                                uhlala = Thread.objects.create(user=mail.user)
                                uhlala.mails.add(mail_obj)
                    else:  # else create brand new thread
                        uhlala = Thread.objects.create(user=mail.user)
                        uhlala.mails.add(mail_obj)
                except KeyError:
                    uhlala = Thread.objects.create(user=mail.user)
                    uhlala.mails.add(mail_obj)
            else:
                logger.error('item processor failed', exc_info=True, extra={
                    'request': hiren.text,
                })


@task()
def incoming_mail():
    """
    Check incoming mail
    :return:
    """
    with transaction.atomic():
        mails = MailGun.objects.all().select_related()
        for mail in mails:
            bunny = requests.get('https://api.mailgun.net/v3/%s/events' % mail.name,
                                 auth=("api", mail.key), params={"event": "stored"})
            if bunny.status_code == 200:
                bugs = bunny.json()
                if bugs['items']:
                    items_process(bugs['items'], mail, mail.encryption)
                    while True:  # pagination
                        nisha = requests.get(bugs['paging']['next'], auth=('api', mail.key))
                        if nisha.status_code == 200:
                            hiren = nisha.json()
                            if hiren['items']:
                                items_process(hiren['items'], mail, mail.encryption)
                            else:
                                break
            else:
                logger.error('get mail failed!', exc_info=True, extra={
                    'request': bunny.text,
                })



