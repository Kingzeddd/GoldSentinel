from django.db import models
from base.models.helpers.named_date_time_model import NamedDateTimeModel


class AlertModel(NamedDateTimeModel):
    CRITICALITY_LEVELS = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyen'),
        ('HIGH', 'Élevé'),
        ('CRITICAL', 'Critique'),
    ]

    ALERT_TYPES = [
        ('CLANDESTINE_SITE', 'Site clandestin détecté'),
        ('SITE_EXPANSION', 'Expansion possible d\'un site existant'),
        ('SUSPICIOUS_ACTIVITY', 'Activité suspecte détectée par IA'),
        ('NEW_SITE', 'Nouveau site détecté près d\'une rivière'),
        ('PROTECTED_ZONE_BREACH', 'Activité en zone protégée'),
        ('WATER_POLLUTION', 'Pollution d\'eau détectée'),
        ('DEFORESTATION_ALERT', 'Déforestation majeure détectée'),
    ]

    ALERT_STATUS = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Accusée'),
        ('RESOLVED', 'Résolue'),
        ('FALSE_ALARM', 'Fausse alerte'),
    ]

    # Relations
    detection = models.ForeignKey('detection.DetectionModel', on_delete=models.CASCADE, related_name='alerts')
    region = models.ForeignKey('region.RegionModel', on_delete=models.CASCADE)

    # Détails alerte
    level = models.CharField(max_length=20, choices=CRITICALITY_LEVELS)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    message = models.TextField()
    alert_status = models.CharField(max_length=20, choices=ALERT_STATUS, default='ACTIVE')

    # Traitement
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Attribution
    assigned_to = models.ForeignKey('account.UserModel', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='assigned_alerts')

    class Meta:
        db_table = 'mining_alerts'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['level', 'alert_status']),
            models.Index(fields=['alert_type', 'region']),
            models.Index(fields=['region', 'sent_at']),
        ]

    def __str__(self):
        return f"Alerte {self.level} - {self.get_alert_type_display()} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"