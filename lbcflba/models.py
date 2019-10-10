import enum

from django.conf import settings
from django.db import models


class Transaction(models.Model):
    # , related_name="+": create no backward relation
    # see https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.ForeignKey.related_name
    source = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    destination = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    text = models.TextField()
    time = models.DateTimeField()
    status = models.PositiveSmallIntegerField()


class Status(enum.Enum):
    waiting = 0
    processed = 1

    @classmethod
    def parse(cls, n: int):
        if getattr(cls, "value_mapping", None) is None:
            Status.value_mapping = {status.value: status.name for status in cls}
        return Status.value_mapping.get(n, None)