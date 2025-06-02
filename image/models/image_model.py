from django.db import models
from django.contrib.gis.db import models as gis_models
from base.models.helpers.named_date_time_model import NamedDateTimeModel


class ImageModel(NamedDateTimeModel):
    SATELLITE_SOURCES = [
        ('SENTINEL2', 'Sentinel-2'),
        ('LANDSAT8', 'Landsat-8'),
        ('LANDSAT9', 'Landsat-9'),
    ]

    PROCESSING_STATUS = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'Traitement en cours'),
        ('COMPLETED', 'Terminé'),
        ('ERROR', 'Erreur'),
    ]

    region = models.ForeignKey('region.RegionModel', on_delete=models.CASCADE)

    # Métadonnées satellite
    capture_date = models.DateField()
    satellite_source = models.CharField(max_length=50, choices=SATELLITE_SOURCES)
    cloud_coverage = models.FloatField(help_text="Pourcentage 0-100")
    resolution = models.FloatField(help_text="Résolution en mètres", default=10)

    # ADAPTATION GOOGLE EARTH ENGINE
    gee_asset_id = models.CharField(max_length=200, unique=True, default="TEMP_ASSET_ID", help_text="ID asset Google Earth Engine")
    gee_collection = models.CharField(max_length=100, default='COPERNICUS/S2_SR', help_text="Collection GEE")

    # Indices spectraux calculés via GEE (stockage JSON)
    ndvi_data = models.JSONField(null=True, blank=True, help_text="Données NDVI calculées")
    ndwi_data = models.JSONField(null=True, blank=True, help_text="Données NDWI calculées")
    ndti_data = models.JSONField(null=True, blank=True, help_text="Données NDTI calculées")

    # Statistiques des indices
    ndvi_mean = models.FloatField(null=True, blank=True)
    ndwi_mean = models.FloatField(null=True, blank=True)
    ndti_mean = models.FloatField(null=True, blank=True)

    # Zone couverte (fixe pour Bondoukou)
    covered_area = gis_models.PolygonField(srid=4326, null=True, blank=True)
    center_lat = models.FloatField(default=8.0402)
    center_lon = models.FloatField(default=-2.8000)

    # Traitement
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='PENDING')
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True, null=True)

    # Utilisateur ayant demandé l'analyse
    requested_by = models.ForeignKey('account.UserModel', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'satellite_images'
        ordering = ['-capture_date']
        indexes = [
            models.Index(fields=['capture_date', 'processing_status']),
            models.Index(fields=['gee_asset_id']),
        ]

    def __str__(self):
        return f"{self.name} - {self.satellite_source} - {self.capture_date}"