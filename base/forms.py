from django.forms import ModelForm
from .models import MailGun, Pgpkey
from mail.models import Contact


class MailGunForm(ModelForm):
    class Meta:
        model = MailGun
        exclude = ('user', )


class PgpKeyForm(ModelForm):
    class Meta:
        model = Pgpkey
        exclude = ('user', )


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        exclude = ('user', 'm_type')

