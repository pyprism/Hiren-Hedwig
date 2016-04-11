from django.db import models


class Domain(models.Model):
    name = models.CharField(max_length=253)


class API(models.Model):
    domain = models.ForeignKey('Domain')
    key = models.CharField(max_length=500)


class Message(models.Model):
    types = (
        ('incoming', 'Inbox'),
        ('outgoing', 'Sent'),
        ('draft', 'Draft')
    )
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)
    _from = models.EmailField()
    to = models.EmailField(default='')
    subject = models.CharField(max_length=255, default='')
    message = models.TextField(default='')
    message_id = models.CharField(max_length=500)
    cc = models.EmailField(default='')
    bcc = models.EmailField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    type = models.CharField(max_length=5, choices=types)


class ThreadedView(models.Model):
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)
    message = models.ManyToManyField('Message')


class UrlKey(models.Model):
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)
    mailgun_key = models.CharField(max_length=500)
