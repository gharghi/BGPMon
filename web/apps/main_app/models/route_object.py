from .asn import Asn
from .prefix import Prefix
from django.db import models

class RouteObject(models.Model):
    asn = models.ForeignKey(Asn, on_delete=models.CASCADE)
    prefix = models.ForeignKey(Prefix, on_delete=models.CASCADE)

    def __str__(self):
        return self.prefix_id + '/' + self.asn_id