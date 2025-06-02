from rest_framework import serializers
from detection.models.detection_model import DetectionModel


class DetectionSerializer(serializers.ModelSerializer):
    image_name = serializers.CharField(source='image.name', read_only=True)
    image_capture_date = serializers.DateField(source='image.capture_date', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    validated_by_name = serializers.CharField(source='validated_by.get_full_name', read_only=True)

    class Meta:
        model = DetectionModel
        fields = ['id', 'image', 'image_name', 'image_capture_date', 'region', 'region_name',
                  'latitude', 'longitude', 'detection_type', 'confidence_score', 'area_hectares',
                  'ndvi_anomaly_score', 'ndwi_anomaly_score', 'ndti_anomaly_score',
                  'validation_status', 'validated_by', 'validated_by_name', 'validated_at',
                  'detection_date', 'algorithm_version']
        read_only_fields = ['id', 'image_name', 'image_capture_date', 'region_name',
                            'validated_by_name', 'detection_date', 'confidence_score']
