from rest_framework import serializers
from region.models.region_model import RegionModel

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionModel
        fields = ['id', 'name', 'code', 'area_km2', 'center_lat', 'center_lon',
                 'monitored_zones', 'authorized_sites', 'protected_zones']
        read_only_fields = ['id']