from django.db import models
from web.apps.jwt_store.models import User


class Asn(models.Model):
    asn = models.IntegerField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.asn
