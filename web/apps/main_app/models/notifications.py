from django.db import models

from web.apps.jwt_store.models import User


class Notifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    type = models.IntegerField(default=0)
    path = models.TextField(null=True)
    prefix = models.CharField(max_length=60, null=True)
    asn = models.IntegerField(null=True)
    status = models.BooleanField(default=False)
    time = models.BigIntegerField()

    def __str__(self):
        return self.type
