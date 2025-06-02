from django.db import models
from django.utils.translation import gettext_lazy as _ # Import gettext_lazy
from base.models.helpers.named_date_time_model import NamedDateTimeModel


class AlertModel(NamedDateTimeModel):
    class CriticalityLevelChoices(models.TextChoices):
        LOW = 'LOW', _('Faible')
        MEDIUM = 'MEDIUM', _('Moyen')
        HIGH = 'HIGH', _('Élevé')
        CRITICAL = 'CRITICAL', _('Critique')

    class AlertTypeChoices(models.TextChoices):
        CLANDESTINE_SITE = 'CLANDESTINE_SITE', _('Site clandestin détecté')
        SITE_EXPANSION = 'SITE_EXPANSION', _('Expansion possible d\'un site existant')
        SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY', _('Activité suspecte détectée par IA')
        NEW_SITE = 'NEW_SITE', _('Nouveau site détecté près d\'une rivière')
        PROTECTED_ZONE_BREACH = 'PROTECTED_ZONE_BREACH', _('Activité en zone protégée')
        WATER_POLLUTION = 'WATER_POLLUTION', _('Pollution d\'eau détectée')
        DEFORESTATION_ALERT = 'DEFORESTATION_ALERT', _('Déforestation majeure détectée')

    class AlertStatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        ACKNOWLEDGED = 'ACKNOWLEDGED', _('Accusée') # Corrected spelling from 'Accusée' if it was a typo, or keep as is
        RESOLVED = 'RESOLVED', _('Résolue')
        FALSE_ALARM = 'FALSE_ALARM', _('Fausse alerte')

    # Relations
    detection = models.ForeignKey('detection.DetectionModel', on_delete=models.CASCADE, related_name='alerts')
    region = models.ForeignKey('region.RegionModel', on_delete=models.CASCADE)

    # Détails alerte
    level = models.CharField(max_length=20, choices=CriticalityLevelChoices.choices, default=CriticalityLevelChoices.MEDIUM)
    alert_type = models.CharField(max_length=50, choices=AlertTypeChoices.choices, default=AlertTypeChoices.SUSPICIOUS_ACTIVITY)
    message = models.TextField()
    alert_status = models.CharField(max_length=20, choices=AlertStatusChoices.choices, default=AlertStatusChoices.ACTIVE)

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