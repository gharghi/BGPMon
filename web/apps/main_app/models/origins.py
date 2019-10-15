from django.db import models
from .prefix import Prefix


class Origins(models.Model):
    prefix = models.ForeignKey(Prefix, on_delete=models.CASCADE,related_name='origins')
    origin = models.IntegerField(blank=True, null= True)

    def __str__(self):
        return self.prefix
