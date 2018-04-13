from django.forms import ModelForm
from .models import MailGun, Pgpkey


class MailGunForm(ModelForm):
    class Meta:
        model = MailGun
        exclude = ('user', )


class PgpKeyForm(ModelForm):
    class Meta:
        model = Pgpkey
        exclude = ('user', )

