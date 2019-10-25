from django.db import models
from web.apps.jwt_store.models import User


class NotificationRule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    phone = models.BigIntegerField(null=True)
    email = models.CharField(max_length=60, null=True)
    hijacked = models.BooleanField(default=0)
    hijacking = models.BooleanField(default=0)
    transited = models.BooleanField(default=0)
    transiting = models.BooleanField(default=0)

    def __str__(self):
        return self.phone
