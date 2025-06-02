from django.db import models
from django.contrib.gis.db import models as gis_models
from base.models.helpers.date_time_model import DateTimeModel
from config.detection_settings import DetectionConfig # Import DetectionConfig


class DetectionModel(DateTimeModel):
    DETECTION_TYPES = [
        ('MINING_SITE', 'Site minier'),
        ('WATER_POLLUTION', 'Pollution eau'),
        ('DEFORESTATION', 'Déforestation'),
        ('SOIL_DISTURBANCE', 'Perturbation sol'),
    ]

    VALIDATION_STATUS = [
        ('DETECTED', 'Détecté'),
        ('VALIDATED', 'Validé'),
        ('FALSE_POSITIVE', 'Faux positif'),
        ('CONFIRMED', 'Confirmé'),
    ]

    # Relations
    image = models.ForeignKey('image.ImageModel', on_delete=models.CASCADE, related_name='detections')
    region = models.ForeignKey('region.RegionModel', on_delete=models.CASCADE)

    # Coordonnées précises
    latitude = models.FloatField()
    longitude = models.FloatField()
    zone_geometry = gis_models.PolygonField(srid=4326, null=True, blank=True)

    # Détection
    detection_type = models.CharField(max_length=30, choices=DETECTION_TYPES)
    confidence_score = models.FloatField(help_text="Score de confiance 0.0-1.0")
    area_hectares = models.FloatField(help_text="Surface estimée en hectares", default=0)

    # Scores des indices (base pour confidence_score)
    ndvi_anomaly_score = models.FloatField(null=True, blank=True)
    ndwi_anomaly_score = models.FloatField(null=True, blank=True)
    ndti_anomaly_score = models.FloatField(null=True, blank=True)

    # Validation
    validation_status = models.CharField(max_length=20, choices=VALIDATION_STATUS, default='DETECTED')
    validated_by = models.ForeignKey('account.UserModel', on_delete=models.SET_NULL, null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)

    # Métadonnées traitement
    detection_date = models.DateTimeField(auto_now_add=True)
    algorithm_version = models.CharField(max_length=50, default="NDVI_NDWI_NDTI_v1.0")

    class Meta:
        db_table = 'mining_detections'
        ordering = ['-detection_date']
        indexes = [
            models.Index(fields=['confidence_score']),
            models.Index(fields=['detection_type', 'validation_status']),
            models.Index(fields=['region', 'detection_date']),
        ]

    def __str__(self):
        return f"{self.detection_type} - Score: {self.confidence_score:.2f} - {self.detection_date.strftime('%Y-%m-%d')}"

    def calculate_confidence_score(self):
        """
        Calcul du score de confiance basé sur les indices spectraux d'anomalie.
        Cette méthode calcule ce qui est parfois référé comme 'anomaly_confidence'.
        Le score final de la détection peut ensuite combiner cela avec d'autres sources (ex: TF).
        """
        # Utiliser les poids depuis DetectionConfig
        # Assurer que les scores None sont traités comme 0.0 dans le calcul
        score = (
            DetectionConfig.ANOMALY_CONFIDENCE_WEIGHT_NDVI * (self.ndvi_anomaly_score or 0.0) +
            DetectionConfig.ANOMALY_CONFIDENCE_WEIGHT_NDWI * (self.ndwi_anomaly_score or 0.0) +
            DetectionConfig.ANOMALY_CONFIDENCE_WEIGHT_NDTI * (self.ndti_anomaly_score or 0.0)
        )

        # La vérification `if not all(...)` n'est plus strictement nécessaire si on traite les None en 0.0,
        # car si tous sont None (ou 0.0), le score sera 0.0.
        # Si au moins un score est non-None et positif, le score sera > 0.
        # Cependant, si la logique métier exige qu'un score nul soit retourné si *l'un* des scores est manquant (None),
        # alors la vérification `if self.ndvi_anomaly_score is None or ...: return 0.0` serait plus appropriée.
        # Pour l'instant, on suppose que les scores manquants (None) contribuent à 0 à la somme pondérée.

        return min(max(score, 0.0), 1.0)  # Clamp entre 0 et 1