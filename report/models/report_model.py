from django.db import models
from django.contrib.gis.db import models as gis_models


from base.models.helpers.named_date_time_model import NamedDateTimeModel
from base.models.helpers.date_time_model import DateTimeModel

from account.models.user_model import UserModel
from region.models.region_model import RegionModel



class ReportModel(NamedDateTimeModel):
    """
    Représente un rapport généré dans le système.
    Ce pourrait être un rapport PDF, CSV, ou un rapport de synthèse.
    """
    REPORT_TYPES = [
        ('SUMMARY', 'Summary Report'),
        ('REGION_DETAIL', 'Regional Detail Report'),
        ('ALERT_SUMMARY', 'Alerts Summary Report'),
        ('DEFORESTATION_TREND', 'Deforestation Trend Report'),
        ('WATER_QUALITY_TREND', 'Water Quality Trend Report'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES,
                                   help_text="Type of report generated")
    generated_by = models.ForeignKey(UserModel, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='generated_reports')
    # Les rapports peuvent être liés à une région spécifique
    region = models.ForeignKey(RegionModel, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='reports')
    # Date de début et de fin pour la période couverte par le rapport
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # Fichier du rapport généré (ex: PDF, CSV)
    report_file = models.FileField(upload_to='reports/%Y/%m/', blank=True, null=True,
                                   help_text="Generated report file (e.g., PDF, CSV)")
    # URL externe si le rapport est stocké ailleurs (ex: Google Drive)
    external_url = models.URLField(max_length=500, blank=True, null=True,
                                   help_text="External URL if report is hosted elsewhere")

    # Un champ pour un bref résumé du rapport
    summary = models.TextField(blank=True,
                               help_text="A brief summary or key findings of the report")

    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'region']),
            models.Index(fields=['generated_by', 'created_at']),
        ]

    def __str__(self):
        return f"Report {self.name} - {self.report_type} for {self.region.name if self.region else 'All Regions'} ({self.created_at.strftime('%Y-%m-%d')})"





