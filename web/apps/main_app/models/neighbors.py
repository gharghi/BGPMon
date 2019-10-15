from django.db import models
from .asn import Asn


class Neighbors(models.Model):
    asn = models.ForeignKey(Asn, on_delete=models.CASCADE)
    neighbor = models.IntegerField(default=0)
    type = models.IntegerField(default=0)

    def __str__(self):
        return self.asn
