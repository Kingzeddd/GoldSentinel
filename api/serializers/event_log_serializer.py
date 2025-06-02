from rest_framework import serializers

from report.models.event_log_model import EventLogModel


class EventLogSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    detection_info = serializers.SerializerMethodField()
    time_since = serializers.SerializerMethodField()

    class Meta:
        model = EventLogModel
        fields = ['id', 'event_type', 'event_type_display', 'message',
                  'user', 'user_name', 'detection', 'detection_info',
                  'alert', 'region', 'metadata', 'created_at', 'time_since']
        read_only_fields = ['id', 'created_at']

    def get_detection_info(self, obj):
        if obj.detection:
            return {
                'id': obj.detection.id,
                'type': obj.detection.detection_type,
                'confidence': obj.detection.confidence_score
            }
        return None

    def get_time_since(self, obj):
        from django.utils import timezone
        import datetime

        now = timezone.now()
        diff = now - obj.created_at

        if diff.days > 0:
            return f"{diff.days} jours"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h"
        else:
            minutes = diff.seconds // 60
            return f"{minutes}min"