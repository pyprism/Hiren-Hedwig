import os
from celery import Celery
# from utils.tasks import incoming_mail


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hiren.settings')

app = Celery('hiren')
app.config_from_object('django.conf:settings', namespace='CELERY')


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(5.0, 'utils.tasks.incoming_mail()', name='run every 5 minute')


app.autodiscover_tasks()


