from rest_framework import serializers
from alert.models.alert_model import AlertModel


class AlertSerializer(serializers.ModelSerializer):
    detection_info = serializers.SerializerMethodField()
    region_name = serializers.CharField(source='region.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    time_since_created = serializers.CharField(read_only=True)

    class Meta:
        model = AlertModel
        fields = ['id', 'name', 'detection', 'detection_info', 'region', 'region_name',
                  'level', 'alert_type', 'message', 'alert_status', 'sent_at', 'is_read',
                  'assigned_to', 'assigned_to_name', 'time_since_created']
        read_only_fields = ['id', 'detection_info', 'region_name', 'assigned_to_name',
                            'sent_at', 'time_since_created']

    def get_detection_info(self, obj):
        return {
            'id': obj.detection.id,
            'type': obj.detection.detection_type,
            'confidence_score': obj.detection.confidence_score,
            'coordinates': f"{obj.detection.latitude}, {obj.detection.longitude}",
            'area_hectares': obj.detection.area_hectares
        }
