from django.db import models

from base.models.helpers.date_time_model import DateTimeModel


class NamedDateTimeModel(DateTimeModel):

    name = models.CharField(max_length=150)

    class Meta:
        abstract = True