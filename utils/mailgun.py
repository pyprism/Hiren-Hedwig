import requests
import django
import os
import logging
from datetime import datetime, timedelta
from email.utils import parsedate_tz
import tempfile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hiren.settings")
django.setup()

from base.models import MailGun, Cron
from mail.models import Mail, Attachment, Thread
from django.core import files
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task

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


@shared_task
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
                          "h:In-Reply-To": mail.in_reply_to,
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


# BLEACH_VALID_TAGS = ['p', 'b', 'i', 'strike', 'ul', 'li', 'ol', 'br',
#                      'span', 'blockquote', 'hr', 'a', 'img', 'table', 'tbody',
#                      'thead', 'tr', 'th', 'abbr', 'acronym', 'address', 'area', 'bdo',
#                      'big', 'button', 'caption', 'center', 'cite', 'code', 'col', 'colgroup', 'dd', 'del',
#                      'dfn', 'dir', 'div', 'dl', 'dt', 'em', 'fieldset', 'font', 'form', 'h1', 'h2', 'h3', 'h4',
#                      'h5', 'h6', 'hr', 'i', 'input', 'ins', 'kbd', 'label', 'legend', 'map', 'menu', 'optgroup',
#                      'option', 'p', 'pre', 'q', 's', 'samp', 'select', 'small', 'span', 'strike', 'strong', 'sub',
#                      'sup', 'th', 'textarea', 'tfoot', 'tt', 'u', 'var']
# BLEACH_VALID_ATTRS = {
#     'span': ['style', ],
#     'p': ['align', ],
#     'a': ['href', 'rel'],
#     'img': ['src', 'alt', 'style'],
# }
#
# # source https://developers.google.com/gmail/design/reference/supported_css
# BLEACH_VALID_STYLES = ['azimuth', 'background', 'background-blend-mode', 'background-blend-mode', 'background-color', 'background-image',
#                        'background-origin', 'background-position', 'background-repeat', 'background-size', 'border',
#                        'border-bottom', 'border-bottom-color', 'border-bottom-left-radius', 'border-bottom-right-radius',
#                        'border-bottom-style', 'border-bottom-width', 'border-collapse', 'border-color', 'border-left',
#                        'border-left-color', 'border-left-style', 'border-left-width', 'border-radius', 'border-right',
#                        'border-right-color', 'border-right-color', 'border-right-width', 'border-spacing',
#                        'border-style', 'border-top', 'border-top-color', 'border-top-left-radius', 'border-top-right-radius',
#                        'border-top-style', 'border-top-width', 'border-width', 'box-sizing', 'break-after',
#                        'break-before', 'break-inside', 'caption-side', 'clear', 'color', 'column-count',
#                        'column-fill', 'column-gap', 'column-rule', 'column-rule-color', 'column-rule-style',
#                        'column-rule-width', 'column-span', 'column-span', 'columns', 'direction', 'display',
#                        'elevation', 'empty-cells', 'float', 'font', 'font-family', 'font-feature-settings',
#                        'font-kerning', 'font-size', 'font-size-adjust', 'font-stretch', 'font-style', 'font-synthesis',
#                        'font-variant', 'font-variant-alternates', 'font-variant-caps', 'font-variant-caps', 'font-variant-ligatures',
#                        'font-variant-numeric', 'font-weight', 'height', 'image-orientation', 'image-resolution', 'isolation',
#                        'letter-spacing', 'line-height', 'list-style', 'list-style-position', 'list-style-type', 'margin',
#                        'margin-bottom', 'margin-left', 'margin-right', 'margin-right', 'margin-right', 'max-width', 'min-height',
#                        'min-width', 'mix-blend-mode', 'object-fit', 'object-position', 'opacity', 'outline', 'outline-color',
#                        'outline-style', 'outline-width', 'overflow', 'padding', 'padding-bottom', 'padding-left',
#                        'padding-right', 'padding-top', 'pause', 'pause-after', 'pause-before', 'pitch', 'pitch-range',
#                        'quotes', 'richness', 'speak', 'speak-header', 'speak-numeral', 'speak-punctuation', 'speech-rate',
#                        'stress', 'table-layout', 'text-align', 'text-combine-upwrite', 'text-decoration',
#                        'text-decoration-color', 'text-decoration-line', 'text-decoration-skip', 'text-decoration-style',
#                        'text-emphasis', 'text-emphasis-color', 'text-emphasis-style', 'text-indent', 'text-orientation',
#                        'text-overflow', 'text-overflow', 'text-underline-position', 'unicode-bidi', 'vertical-align',
#                        'voice-family', 'width', 'word-spacing', 'writing-mode', 'all', 'screen', 'min-width',
#                        'max-width', 'min-device-width', 'min-device-width', 'orientation', 'min-resolution',
#                        'max-resolution', 'and', 'only']
# =bleach.clean(bunny['body-html'], BLEACH_VALID_TAGS, BLEACH_VALID_ATTRS,
#                                                           BLEACH_VALID_STYLES, strip=True, strip_comments=True),


def items_process(items, mail):
    """
    Process and save incoming mail
    :param items: API response
    :param mail: db object
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
                                               body=bunny['body-html'], state='R',
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


@shared_task
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
                    while True:  # pagination
                        nisha = requests.get(bugs['paging']['next'], auth=('api', mail.key))
                        if nisha.status_code == 200:
                            hiren = nisha.json()
                            if hiren['items']:
                                items_process(hiren['items'], mail)
                            else:
                                break
            else:
                logger.error('get mail failed!', exc_info=True, extra={
                    'request': bunny.text,
                })
        cron.lock = False
        cron.save()



