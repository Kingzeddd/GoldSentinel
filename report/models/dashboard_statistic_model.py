from django.db import models
from django.utils.translation import gettext_lazy as _ # Import gettext_lazy
from base.models.helpers.date_time_model import DateTimeModel
from region.models.region_model import RegionModel


class DashboardStatistic(DateTimeModel):
    """
    Stocke les statistiques agrégées pour le tableau de bord.
    Ces statistiques peuvent être pré-calculées périodiquement
    pour améliorer les performances du tableau de bord.
    """
    class StatisticTypeChoices(models.TextChoices):
        TOTAL_DETECTIONS = 'TOTAL_DETECTIONS', _('Total Detections')
        ACTIVE_ALERTS = 'ACTIVE_ALERTS', _('Active Alerts')
        RESOLVED_ALERTS = 'RESOLVED_ALERTS', _('Resolved Alerts')
        NEW_MINING_SITES = 'NEW_MINING_SITES', _('New Mining Sites')
        DEFORESTATION_HA = 'DEFORESTATION_HA', _('Total Deforestation (Ha)')
        WATER_POLLUTION_INCIDENTS = 'WATER_POLLUTION_INCIDENTS', _('Water Pollution Incidents')
        VALIDATED_DETECTIONS = 'VALIDATED_DETECTIONS', _('Validated Detections')
        # Add any other planned statistic types here

    statistic_type = models.CharField(
        max_length=50,
        choices=StatisticTypeChoices.choices,
        # unique=True removed here, handled by unique_together in Meta
        help_text=_("Type of aggregated statistic")
    )
    value = models.FloatField(help_text=_("Aggregated value for the statistic"))
    # Si la statistique est spécifique à une région, sinon laisser null
    region = models.ForeignKey(RegionModel, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='dashboard_statistics')
    # Période pour laquelle la statistique a été calculée (si applicable)
    date_calculated = models.DateField(
        help_text=_("Date for which this statistic was calculated or applies (e.g., end of month)"))

    class Meta:
        db_table = 'dashboard_statistics'
        verbose_name = _('Dashboard Statistic')
        verbose_name_plural = _('Dashboard Statistics')
        ordering = ['statistic_type', '-date_calculated']
        # Contrainte d'unicité pour les stats régionales/temporelles
        unique_together = ('statistic_type', 'region', 'date_calculated') # This is correct
        indexes = [
            models.Index(fields=['statistic_type', 'date_calculated']),
        ]

    def __str__(self):
        region_name = self.region.name if self.region else _('All Regions')
        # Ensure get_statistic_type_display works with TextChoices
        return f"{self.get_statistic_type_display()} for {region_name} on {self.date_calculated}: {self.value}"