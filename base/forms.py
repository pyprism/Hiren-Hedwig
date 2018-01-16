from django.forms import ModelForm
from .models import MailGun


class MailGunForm(ModelForm):
    class Meta:
        model = MailGun
        exclude = ('user', )

