import requests
import django
import os
# import asyncio
# loop = asyncio.get_event_loop()
# loop.run_in_executor(None, 'task')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hiren.settings")
django.setup()

from base.models import MailGun

def send_mail():
    pass
