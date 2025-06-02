from django.db import models
from base.models.helpers.date_time_model import DateTimeModel
from config.financial_settings import FinancialSettings


class FinancialRiskModel(DateTimeModel):
    RISK_LEVELS = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyen'),
        ('HIGH', 'Élevé'),
        ('CRITICAL', 'Critique'),
    ]

    # Relation 1-1 avec Detection
    detection = models.OneToOneField('detection.DetectionModel', on_delete=models.CASCADE,
                                     related_name='financial_risk')

    # Calculs financiers
    area_hectares = models.FloatField(help_text="Surface affectée en hectares")
    cost_per_hectare = models.FloatField(default=50000, help_text="Coût par hectare en FCFA")
    estimated_loss = models.FloatField(null=True, help_text="Perte estimée en FCFA")

    # Facteurs de risque
    sensitive_zone_distance_km = models.FloatField(default=0, help_text="Distance zones sensibles (km)")
    occurrence_count = models.IntegerField(default=1, help_text="Nombre d'occurrences détectées")

    # Évaluation finale
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)

    class Meta:
        db_table = 'financial_risks'
        ordering = ['-estimated_loss']
        indexes = [
            models.Index(fields=['risk_level', 'estimated_loss']),
        ]

    def __str__(self):
        return f"Risque {self.risk_level} - {self.estimated_loss:,.0f} FCFA"

    def calculate_estimated_loss(self):
        """Calcul basé sur configuration centralisée"""

        # Coût de base depuis configuration
        base_cost = FinancialSettings.DEFAULT_COST_PER_HECTARE

        # Facteur intensité selon indices spectraux
        intensity_factor = self._calculate_intensity_factor()

        # Calcul base
        base_loss = self.area_hectares * base_cost * intensity_factor

        # Facteurs distance et récurrence
        distance_factor = FinancialSettings.get_distance_factor(self.sensitive_zone_distance_km)
        occurrence_factor = min(self.occurrence_count * 0.2 + 1, 2.0)

        # Résultat final
        self.estimated_loss = base_loss * distance_factor * occurrence_factor
        return self.estimated_loss

    def _calculate_intensity_factor(self) -> float:
        """Calcule facteur intensité selon indices spectraux"""
        detection = self.detection
        intensity_factor = 1.0
        settings = FinancialSettings.SPECTRAL_FACTORS

        # NDVI - Déforestation
        if (hasattr(detection, 'ndvi_anomaly_score') and detection.ndvi_anomaly_score and
                detection.ndvi_anomaly_score > settings['ndvi_severe_threshold']):
            intensity_factor += settings['ndvi_factor']

        # NDWI - Pollution eau
        if (hasattr(detection, 'ndwi_anomaly_score') and detection.ndwi_anomaly_score and
                detection.ndwi_anomaly_score > settings['ndwi_pollution_threshold']):
            intensity_factor += settings['ndwi_factor']

        # NDTI - Perturbation sols
        if (hasattr(detection, 'ndti_anomaly_score') and detection.ndti_anomaly_score and
                detection.ndti_anomaly_score > settings['ndti_disturbance_threshold']):
            intensity_factor += settings['ndti_factor']

        return intensity_factor

    def determine_risk_level(self):
        """Utilise configuration centralisée"""
        return FinancialSettings.determine_risk_level_from_loss(self.estimated_loss or 0)