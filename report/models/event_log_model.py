from django.db import models
from base.models.helpers.date_time_model import DateTimeModel
from region.models.region_model import RegionModel
from detection.models.detection_model import DetectionModel
from alert.models.alert_model import AlertModel
from account.models.user_model import UserModel


class EventLogModel(DateTimeModel):
    """
    Enregistre les événements importants du système,
    utilisé pour le suivi et les audits, peut alimenter un flux d'activité.
    """
    EVENT_TYPES = [
        ('DETECTION_CREATED', 'New Detection Created'),
        ('ALERT_GENERATED', 'New Alert Generated'),
        ('ALERT_ACKNOWLEDGED', 'Alert Acknowledged'),
        ('ALERT_RESOLVED', 'Alert Resolved'),
        ('DETECTION_VALIDATED', 'Detection Validated'),
        ('INVESTIGATION_CREATED', 'Investigation Created'),
        ('INVESTIGATION_ASSIGNED', 'Investigation Assigned'),
        ('INVESTIGATION_COMPLETED', 'Investigation Completed'),
        ('ANALYSIS_STARTED', 'Analysis Started'),
        ('ANALYSIS_COMPLETED', 'Analysis Completed'),
        ('USER_LOGIN', 'User Logged In'),
        ('REPORT_GENERATED', 'Report Generated'),
        ('IMAGE_PROCESSED', 'Image Processed'),
        ('SYSTEM_ERROR', 'System Error'),
        ('FINANCIAL_RISK_CALCULATED', 'Financial Risk Calculated'),
        ('FEEDBACK_CREATED', 'Detection Feedback Created'),
    ]

    event_type = models.CharField(max_length=50, choices=EVENT_TYPES,
                                  help_text="Type of system event")
    message = models.TextField(help_text="Detailed description of the event")

    # Liens optionnels vers les objets concernés
    user = models.ForeignKey('account.UserModel', on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='user_events')
    detection = models.ForeignKey('detection.DetectionModel', on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='detection_events')
    alert = models.ForeignKey('alert.AlertModel', on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='alert_events')
    region = models.ForeignKey('region.RegionModel', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='region_events')

    # Métadonnées additionnelles
    metadata = models.JSONField(null=True, blank=True, help_text="Additional event data")

    class Meta:
        db_table = 'event_logs'
        verbose_name = 'Event Log'
        verbose_name_plural = 'Event Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.get_event_type_display()}: {self.message[:50]}..."
