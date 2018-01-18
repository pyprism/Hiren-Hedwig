import requests
import django
import os
import logging
# import asyncio
# loop = asyncio.get_event_loop()
# loop.run_in_executor(None, 'task')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hiren.settings")
django.setup()

from base.models import MailGun, Cron
from mail.models import Mail, Attachment

logger = logging.getLogger(__name__)


def send_mail():
    cron, created = Cron.objects.get_or_create(task='S', lock=False)
    if not cron.lock:
        cron.lock = True
        cron.save()
        mails = Mail.objects.filter(state='Q').select_related('domain')
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
                          "html": mail.body})
                if hiren.status_code == 200:  # catch and report failed mail
                    bunny = hiren.json()
                    mail.message_id = bunny['id']
                    mail.state = 'S'
                    mail.save()
                else:
                    logger.error('Email sending failed!', exc_info=True, extra={
                        'request': hiren.json(),
                    })
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
                if hiren.status_code == 200:
                    bunny = hiren.json()
                    mail.message_id = bunny['id']
                    mail.state = 'S'
                    mail.save()
                else:
                    logger.error('Email sending failed!', exc_info=True, extra={
                        'request': hiren.json(),
                    })
        cron.lock = False
        cron.save()



