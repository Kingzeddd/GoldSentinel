from django.db import models
from base.models.helpers.named_date_time_model import NamedDateTimeModel


class AuthorityModel(NamedDateTimeModel):
    AUTHORITY_CHOICES = [
        ('Administrateur', 'Administrateur'),
        ('Responsable Régional', 'Responsable Régional'),
        ('Agent Terrain', 'Agent Terrain'),
        ('Agent Technique', 'Agent Technique'),
        ('Agent Analyste', 'Agent Analyste'),
    ]

    # name prend une valeur de AUTHORITY_CHOICES
    name = models.CharField(max_length=150, choices=AUTHORITY_CHOICES, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'authority'

    def __str__(self):
        return self.name