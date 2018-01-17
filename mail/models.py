from django.db import models
from base.models import Account


class Contact(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField(max_length=800, null=True)
    email = models.CharField(max_length=500)
    mail_type = (
        ('F', 'From'),
        ('T', 'To'),
    )
    m_type = models.CharField(choices=mail_type, max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





