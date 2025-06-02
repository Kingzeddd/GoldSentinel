from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Polygon
from base.models.helpers.named_date_time_model import NamedDateTimeModel


class RegionModel(NamedDateTimeModel):
    """Administrative regions of Côte d'Ivoire"""

    REGION_CHOICES = [
        ('ZANZAN', 'Zanzan'),
        ('DENGUELE', 'Denguélé'),
        ('BOUNKANI', 'Bounkani'),
        ('BONDOUKOU', 'Bondoukou'),  # Focus zone
    ]

    # Override name field with choices
    name = models.CharField(max_length=50, choices=REGION_CHOICES, unique=True)
    code = models.CharField(max_length=10, unique=True)
    area_km2 = models.FloatField()
    geographic_zone = Polygon.from_bbox((-3.0, 7.9, -2.6, 8.2))#gis_models.PolygonField(srid=4326, null=True, blank=True)

    # Dashboard statistics (updated by system)
    monitored_zones = models.IntegerField(default=0)
    authorized_sites = models.IntegerField(default=0)
    protected_zones = models.IntegerField(default=0)
    center_lat = models.FloatField(null=True, blank=True)
    center_lon = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'regions'
        ordering = ['name']