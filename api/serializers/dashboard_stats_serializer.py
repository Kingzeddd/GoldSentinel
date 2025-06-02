from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer pour statistiques dashboard"""

    # Compteurs principaux
    total_detections = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    pending_investigations = serializers.IntegerField()
    total_financial_risk = serializers.FloatField()

    # Période analysée
    analysis_period_days = serializers.IntegerField()
    last_analysis_date = serializers.DateTimeField()

    # Précision système
    accuracy_rate = serializers.FloatField()
    high_confidence_detections = serializers.IntegerField()

    # Tendances
    detections_trend = serializers.ListField()
    alerts_by_level = serializers.DictField()

    # Zones les plus touchées
    affected_zones = serializers.ListField()
