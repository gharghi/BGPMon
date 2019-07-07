from django.db import models
from .asn import Asn


class Neighbors(models.Model):
    asn = models.ForeignKey(Asn, on_delete=models.CASCADE)
    left = models.IntegerField(blank=True, null= True, default=0)
    right = models.IntegerField(blank=True, null= True, default=0)

    def __str__(self):
        return self.asn
