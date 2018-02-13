from django.forms import ModelForm
from .models import Mail


class MailForm(ModelForm):
    class Meta:
        model = Mail
        exclude = ('user', 'state', 'domain', 'message_id', 'received_datetime', 'in_reply_to')


class MailReplyForward(ModelForm):
    class Meta:
        model = Mail
        exclude = ('user', 'state', 'domain', 'received_datetime', 'message_id')

