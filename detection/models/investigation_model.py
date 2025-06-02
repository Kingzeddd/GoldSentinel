from base.models.helpers.date_time_model import DateTimeModel
from django.db import models
from django.utils.translation import gettext_lazy as _ # Import gettext_lazy

class InvestigationModel(DateTimeModel):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', _('En attente')
        ASSIGNED = 'ASSIGNED', _('Assignée')
        IN_PROGRESS = 'IN_PROGRESS', _('En cours')
        COMPLETED = 'COMPLETED', _('Terminée')

    class ResultChoices(models.TextChoices):
        CONFIRMED = 'CONFIRMED', _('Confirmé')
        FALSE_POSITIVE = 'FALSE_POSITIVE', _('Faux positif')
        NEEDS_MONITORING = 'NEEDS_MONITORING', _('Surveillance nécessaire')
        # Consider adding an 'UNKNOWN' or 'NOT_APPLICABLE' if result can be null before completion

    detection = models.OneToOneField('detection.DetectionModel', on_delete=models.CASCADE)

    # Zone précise d'investigation
    target_coordinates = models.CharField(max_length=50, help_text=_("Coordinates of the target (e.g., '8.0402, -2.8000')"))
    access_instructions = models.TextField(blank=True, help_text=_("Instructions to access the site (e.g., 'Take road X, village Y')"))

    # Assignation
    assigned_to = models.ForeignKey(
        'account.UserModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True, # Allow unassigned investigations
        related_name='assigned_investigations',
        help_text=_("Agent assigned to this investigation")
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        help_text=_("Current status of the investigation")
    )

    # Résultats terrain
    result = models.CharField(
        max_length=20,
        choices=ResultChoices.choices,
        null=True,
        blank=True,
        help_text=_("Result of the field investigation")
    )
    field_notes = models.TextField(blank=True, help_text=_("Notes from the field investigation"))
    investigation_date = models.DateField(null=True, blank=True, help_text=_("Date the investigation was conducted"))

    # Additional fields from previous version in merge
    assigned_at = models.DateTimeField(null=True, blank=True, help_text=_("Timestamp when the investigation was assigned"))
    assigned_by = models.ForeignKey(
        'account.UserModel',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='investigations_coordinated', # Different related_name
        help_text=_("User who assigned the investigation")
    )
    priority = models.CharField(max_length=10, default='MEDIUM', help_text=_("Priority of the investigation (LOW, MEDIUM, HIGH)")) # Assuming choices might be added later
    assignment_notes = models.TextField(blank=True, help_text=_("Notes provided during assignment"))


    class Meta:
        db_table = 'investigations'
        verbose_name = _('Investigation')
        verbose_name_plural = _('Investigations')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'assigned_to']),
            models.Index(fields=['detection', 'status']),
        ]

    def __str__(self):
        return f"Investigation {self.detection.id} - {self.status}"
