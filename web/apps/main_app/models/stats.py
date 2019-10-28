from django.db import models

class Stats(models.Model):
    update_time = models.BigIntegerField(default=0)
    update_count = models.IntegerField(default=0)
    matched_count = models.IntegerField(default=0)

    def __str__(self):
        return self.update_count
