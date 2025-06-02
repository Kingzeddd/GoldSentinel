from rest_framework import serializers
from image.models.image_model import ImageModel


class ImageSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)

    class Meta:
        model = ImageModel
        fields = ['id', 'name', 'capture_date', 'satellite_source', 'cloud_coverage',
                  'resolution', 'gee_asset_id', 'gee_collection', 'processing_status',
                  'processed_at', 'processing_error', 'ndvi_mean', 'ndwi_mean', 'ndti_mean',
                  'region', 'region_name', 'requested_by', 'requested_by_name',
                  'center_lat', 'center_lon', 'created_at']
        read_only_fields = ['id', 'region_name', 'requested_by_name', 'processed_at',
                            'processing_error', 'ndvi_mean', 'ndwi_mean', 'ndti_mean', 'created_at']
