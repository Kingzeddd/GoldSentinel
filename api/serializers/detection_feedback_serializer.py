from rest_framework import serializers
from detection.models.detection_feedback_model import DetectionFeedbackModel


class DetectionFeedbackSerializer(serializers.ModelSerializer):
    detection_info = serializers.SerializerMethodField()
    investigation_info = serializers.SerializerMethodField()
    agent_confidence_display = serializers.CharField(source='get_agent_confidence_display', read_only=True)

    class Meta:
        model = DetectionFeedbackModel
        fields = ['id', 'detection', 'detection_info', 'investigation', 'investigation_info',
                  'original_confidence', 'original_ndvi_score', 'original_ndwi_score',
                  'original_ndti_score', 'ground_truth_confirmed', 'agent_confidence',
                  'agent_confidence_display', 'used_for_training', 'created_at']
        read_only_fields = ['id', 'detection_info', 'investigation_info',
                            'agent_confidence_display', 'created_at']

    def get_detection_info(self, obj):
        return {
            'id': obj.detection.id,
            'type': obj.detection.detection_type,
            'coordinates': f"{obj.detection.latitude}, {obj.detection.longitude}"
        }

    def get_investigation_info(self, obj):
        return {
            'id': obj.investigation.id,
            'status': obj.investigation.status,
            'assigned_to': obj.investigation.assigned_to.get_full_name() if obj.investigation.assigned_to else None
        }
