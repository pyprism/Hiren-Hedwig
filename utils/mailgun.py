import requests
import django
import os
import logging
import bleach
from datetime import datetime, timedelta
from email.utils import parsedate_tz
# import asyncio
# loop = asyncio.get_event_loop()
# loop.run_in_executor(None, 'task')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hiren.settings")
django.setup()

from base.models import MailGun, Cron
from mail.models import Mail, Attachment

logger = logging.getLogger(__name__)


def to_datetime(datestring):
    """
    convert rfc 2822 datetime format to django supported format
    :param datestring:
    :return:
    """
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])


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


BLEACH_VALID_TAGS = ['p', 'b', 'i', 'strike', 'ul', 'li', 'ol', 'br',
                     'span', 'blockquote', 'hr', 'a', 'img', 'table', 'tbody',
                     'thead', 'tr', 'th', 'abbr', 'acronym', 'address', 'area', 'bdo',
                     'big', 'button', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
                     'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'fieldset', 'font', 'form', 'h1', 'h2', 'h3', 'h4',
                     'h5', 'h6', 'hr', 'i', 'input', 'ins', 'kbd', 'label', 'legend', 'map', 'menu', 'optgroup',
                     'option', 'p', 'pre', 'q', 's', 'samp', 'select', 'small', 'span', 'strike', 'strong', 'sub',
                     'sup', 'th', 'textarea', 'tfoot', 'tt', 'u', 'var']
BLEACH_VALID_ATTRS = {
    'span': ['style', ],
    'p': ['align', ],
    'a': ['href', 'rel'],
    'img': ['src', 'alt', 'style'],
}
# BLEACH_VALID_STYLES = ['color', 'cursor', 'float', 'margin']


def items_process(items, mail):
    """
    Process and save incoming mail
    :param items: API response
    :param mail: db object
    :return:
    """
    for item in items:
        if not Mail.objects.filter(message_id=item['message']['headers']['message-id']).exists():  # TODO regex domain name
            hiren = requests.get(item['storage']['url'], auth=('api', mail.key))
            if hiren.status_code == 200:
                bunny = hiren.json()
                Mail.objects.create(domain=mail, user=mail.user, mail_from=bunny['From'],
                                    mail_to=bunny['To'], subject=bunny['subject'],
                                    message_id=item['message']['headers']['message-id'], body=bunny['body-html'],
                                    sane_body=bleach.clean(bunny['body-html'], BLEACH_VALID_TAGS, BLEACH_VALID_ATTRS, strip=True),
                                    state='R', received_datetime=to_datetime(bunny['Date']))
            else:
                logger.error('item processor failed', exc_info=True, extra={
                    'request': hiren.json(),
                })


def get_mail():
    cron, created = Cron.objects.get_or_create(task='C', lock=False)
    if not cron.lock:
        cron.lock = True
        cron.save()
        mails = MailGun.objects.all().select_related()
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
            else:
                logger.error('get mail failed!', exc_info=True, extra={
                    'request': bunny.json(),
                })
        cron.lock = False
        cron.save()



