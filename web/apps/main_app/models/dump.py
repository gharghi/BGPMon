from django.db import models


class IPField(models.BinaryField):
    def db_type(self, connection):
        return 'varbinary(128)'


class Dump(models.Model):
    time = models.BigIntegerField()
    asn = models.IntegerField(null=True)
    network = IPField(max_length=60)
    path = models.TextField( null=True)
    community = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.network
