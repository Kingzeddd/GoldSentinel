from django.db import models
from base.models.helpers.date_time_model import DateTimeModel
from region.models.region_model import RegionModel


class DashboardStatistic(DateTimeModel):
    """
    Stocke les statistiques agrégées pour le tableau de bord.
    Ces statistiques peuvent être pré-calculées périodiquement
    pour améliorer les performances du tableau de bord.
    """
    STAT_TYPES = [
        ('TOTAL_DETECTIONS', 'Total Detections'),
        ('ACTIVE_ALERTS', 'Active Alerts'),
        ('RESOLVED_ALERTS', 'Resolved Alerts'),
        ('NEW_MINING_SITES', 'New Mining Sites'),
        ('DEFORESTATION_HA', 'Total Deforestation (Ha)'),
        ('WATER_POLLUTION_INCIDENTS', 'Water Pollution Incidents'),
        ('VALIDATED_DETECTIONS', 'Validated Detections'),
    ]

    statistic_type = models.CharField(max_length=50, choices=STAT_TYPES, unique=True, # Peut être unique si c'est une stat globale
                                      help_text="Type of aggregated statistic")
    value = models.FloatField(help_text="Aggregated value for the statistic")
    # Si la statistique est spécifique à une région, sinon laisser null
    region = models.ForeignKey(RegionModel, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='dashboard_statistics')
    # Période pour laquelle la statistique a été calculée (si applicable)
    date_calculated = models.DateField(
        help_text="Date for which this statistic was calculated or applies (e.g., end of month)")

    class Meta:
        db_table = 'dashboard_statistics'
        verbose_name = 'Dashboard Statistic'
        verbose_name_plural = 'Dashboard Statistics'
        ordering = ['statistic_type', '-date_calculated']
        # Contrainte d'unicité pour les stats régionales/temporelles
        unique_together = ('statistic_type', 'region', 'date_calculated')
        indexes = [
            models.Index(fields=['statistic_type', 'date_calculated']),
        ]

    def __str__(self):
        region_name = self.region.name if self.region else 'All Regions'
        return f"{self.get_statistic_type_display()} for {region_name} on {self.date_calculated}: {self.value}"