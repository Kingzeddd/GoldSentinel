from rest_framework import serializers
from alert.models.financial_risk_model import FinancialRiskModel


class FinancialRiskSerializer(serializers.ModelSerializer):
    detection_info = serializers.SerializerMethodField()

    class Meta:
        model = FinancialRiskModel
        fields = ['id', 'detection', 'detection_info', 'area_hectares', 'cost_per_hectare',
                  'estimated_loss', 'sensitive_zone_distance_km', 'occurrence_count',
                  'risk_level', 'created_at']
        read_only_fields = ['id', 'detection_info', 'estimated_loss', 'risk_level', 'created_at']

    def get_detection_info(self, obj):
        return {
            'id': obj.detection.id,
            'type': obj.detection.detection_type,
            'confidence_score': obj.detection.confidence_score,
            'coordinates': f"{obj.detection.latitude}, {obj.detection.longitude}"
        }
