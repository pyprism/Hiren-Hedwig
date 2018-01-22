import requests
import django
import os
import logging
import bleach
# import asyncio
# loop = asyncio.get_event_loop()
# loop.run_in_executor(None, 'task')
# time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(1516544803.913727))
# bleach.clean(form.cleaned_data['message'],
#                        tags=ALLOWED_TAGS,
#                        attributes=ALLOWED_ATTRIBUTES,
#                        styles=ALLOWED_STYLES,
#                        strip=False, strip_comments=True)

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


def items_process(items, mail):
    for item in items:
        if not Mail.objects.filter(message_id=item['message']['headers']['message-id']).exists():  # TODO regex domain name
            hiren = requests.get(item['storage']['url'], auth=('api', mail.key))
            if hiren.status_code == 200:
                bunny = hiren.json()


def get_mail():
    cron, created = Cron.objects.get_or_create(task='C', lock=False)
    if not cron.lock:
        cron.lock = True
        cron.save()
        mails = MailGun.objects.all()
        for mail in mails:
            bunny = requests.get('https://api.mailgun.net/v3/%s/events' % mail.name,
                                 auth=("api", mail.key), params={"event": "stored"})
            if bunny.status_code == 200:
                bugs = bunny.json()
                if bugs['items']:
                    items_process(bugs['items'], mail)
                    while True:  # paging
                        nisha = requests.get(bugs['paging']['next'], auth=('api', mail.key))
                        if nisha.status_code == 200:
                            hiren = nisha.json()
                            if hiren['items']:
                                items_process(hiren['items'], mail)
                            else:
                                break

            #         for i in bugs['items']:
            # hiren = requests.get('https://api.mailgun.net/v3/domains//messages/',
            #                      auth=("api", ''))
            # print(hiren.status_code)
            # # print(hiren.json())
            # print(hiren.text)
    # else:
    #     print("no")

    # domain = ""
    # key = ""
    # url = "https://api.mailgun.net/v3/domains/%s/messages/%s"
    # url = url % (domain, key)
    # hiren = requests.get(url, auth=("api", ''), headers=headers)
    # print(hiren.status_code)
    # # print(hiren.json())
    # print(hiren.text)
    # print(hiren.content)


get_mail()



