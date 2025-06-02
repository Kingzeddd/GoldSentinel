from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import datetime, timedelta


from api.serializers.event_log_serializer import EventLogSerializer
from report.models.event_log_model import EventLogModel

from permissions.CanViewLogs import CanViewLogs
class EventLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [CanViewLogs]
    """
    ViewSet pour les logs d'événements système
    - GET /api/v1/events/ - Tous les événements
    - GET /api/v1/events/recent/ - Événements récents
    - GET /api/v1/events/by-type/ - Par type d'événement
    """
    queryset = EventLogModel.objects.all()
    serializer_class = EventLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event_type', 'user', 'region']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'], url_path='recent')
    def recent_events(self, request):
        """Événements des dernières 24h"""
        yesterday = datetime.now() - timedelta(hours=24)
        recent = self.queryset.filter(created_at__gte=yesterday)
        serializer = self.get_serializer(recent, many=True)

        return Response({
            'count': recent.count(),
            'period': '24 heures',
            'results': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='by-type')
    def events_by_type(self, request):
        """Comptage événements par type"""
        from django.db.models import Count

        stats = (self.queryset
                 .values('event_type')
                 .annotate(count=Count('id'))
                 .order_by('-count'))

        # Conversion avec labels
        results = []
        for stat in stats:
            event_choice = next((choice for choice in EventLogModel.EVENT_TYPES if choice[0] == stat['event_type']), None)
            results.append({
                'event_type': stat['event_type'],
                'label': event_choice[1] if event_choice else stat['event_type'],
                'count': stat['count']
            })

        return Response({
            'total_events': self.queryset.count(),
            'by_type': results
        })
