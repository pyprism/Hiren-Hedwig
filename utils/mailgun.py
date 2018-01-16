import requests
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hiren.settings")
django.setup()

from base.models import MailGun
