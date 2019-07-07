from web.apps.jwt_store.models import User
from django.db import models
from web.apps.main_app.validation.ip_validation import validate_ipv46_network, validate_ipv46_address

class IPField(models.BinaryField):
    def db_type(self, connection):
        return 'varbinary(128)'


class Prefix(models.Model):
    prefix = models.CharField(max_length=60, validators=[validate_ipv46_network])
    network = IPField(max_length=60, null=True, validators=[validate_ipv46_address])
    broadcast = IPField(max_length=60, null=True, validators=[validate_ipv46_address])
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.prefix