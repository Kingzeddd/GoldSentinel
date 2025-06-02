from rest_framework import serializers
from detection.models.investigation_model import InvestigationModel


class InvestigationSerializer(serializers.ModelSerializer):
    detection_info = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)

    class Meta:
        model = InvestigationModel
        fields = [
            'id', 'detection', 'detection_info', 'target_coordinates',
            'access_instructions', 'assigned_to', 'assigned_to_name',
            'status', 'status_display', 'result', 'result_display',
            'field_notes', 'investigation_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'detection_info', 'assigned_to_name',
            'status_display', 'result_display', 'created_at', 'updated_at'
        ]

    def get_detection_info(self, obj):
        if obj.detection:
            return {
                'id': obj.detection.id,
                'type': obj.detection.detection_type,
                'confidence_score': obj.detection.confidence_score,
                'area_hectares': obj.detection.area_hectares,
                'detection_date': obj.detection.detection_date.strftime('%Y-%m-%d %H:%M')
            }
        return None

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None
