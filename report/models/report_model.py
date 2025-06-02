from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _ # Import gettext_lazy

from base.models.helpers.named_date_time_model import NamedDateTimeModel
# DateTimeModel is not directly used by ReportModel if NamedDateTimeModel already inherits it.
# from base.models.helpers.date_time_model import DateTimeModel

from account.models.user_model import UserModel
from region.models.region_model import RegionModel



class ReportModel(NamedDateTimeModel):
    """
    Représente un rapport généré dans le système.
    Ce pourrait être un rapport PDF, CSV, ou un rapport de synthèse.
    """
    class ReportTypeChoices(models.TextChoices):
        SUMMARY = 'SUMMARY', _('Summary Report')
        REGION_DETAIL = 'REGION_DETAIL', _('Regional Detail Report')
        ALERT_SUMMARY = 'ALERT_SUMMARY', _('Alerts Summary Report')
        DEFORESTATION_TREND = 'DEFORESTATION_TREND', _('Deforestation Trend Report')
        WATER_QUALITY_TREND = 'WATER_QUALITY_TREND', _('Water Quality Trend Report')
        # Add more types as needed

    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        ERROR = 'ERROR', _('Error')

    class FileFormatChoices(models.TextChoices):
        CSV = 'CSV', _('CSV')
        PDF = 'PDF', _('PDF')
        # Add other formats if needed

    report_type = models.CharField(
        max_length=50,
        choices=ReportTypeChoices.choices,
        default=ReportTypeChoices.SUMMARY, # Or another sensible default
        help_text=_("Type of report generated")
    )
    generated_by = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports'
    )
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
    summary = models.TextField(
        blank=True,
        help_text=_("A brief summary or key findings of the report")
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        help_text=_("Generation status of the report")
    )
    file_format = models.CharField(
        max_length=10,
        choices=FileFormatChoices.choices,
        default=FileFormatChoices.CSV,
        help_text=_("File format of the generated report")
    )
    processing_error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Details if an error occurred during report generation"
    )

    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'region']),
            models.Index(fields=['generated_by', 'created_at']),
            models.Index(fields=['status', 'report_type']), # New index
        ]

    def __str__(self):
        return f"Report {self.name} - {self.report_type} for {self.region.name if self.region else 'All Regions'} ({self.created_at.strftime('%Y-%m-%d')})"





