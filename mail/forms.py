from django.forms import ModelForm
from .models import Mail


class MailForm(ModelForm):
    class Meta:
        model = Mail
        exclude = ('user', 'state', 'domain', 'message_id', 'received_datetime')

