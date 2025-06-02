from base.models.helpers.date_time_model import DateTimeModel
from django.db import models

class InvestigationModel(DateTimeModel):
    INVESTIGATION_STATUS = [
        ('PENDING', 'En attente'),
        ('ASSIGNED', 'Assignée'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminée'),
    ]

    INVESTIGATION_RESULT = [
        ('CONFIRMED', 'Confirmé'),
        ('FALSE_POSITIVE', 'Faux positif'),
        ('NEEDS_MONITORING', 'Surveillance nécessaire'),
    ]

    detection = models.OneToOneField('detection.DetectionModel', on_delete=models.CASCADE)

    # Zone précise d'investigation
    target_coordinates = models.CharField(max_length=50)  # "8.0402, -2.8000"
    access_instructions = models.TextField(blank=True)  # "Prendre route X, village Y"

    # Assignation
    assigned_to = models.ForeignKey(
        'account.UserModel',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_investigations'  # 🔧 Ajout du related_name ici
    )
    status = models.CharField(max_length=20, choices=INVESTIGATION_STATUS, default='PENDING')

    # Résultats terrain
    result = models.CharField(max_length=20, choices=INVESTIGATION_RESULT, null=True, blank=True)
    field_notes = models.TextField(blank=True)
    investigation_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'investigations'
        verbose_name = 'Investigation'
        verbose_name_plural = 'Investigations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'assigned_to']),
            models.Index(fields=['detection', 'status']),
        ]

    def __str__(self):
        return f"Investigation {self.detection.id} - {self.status}"
