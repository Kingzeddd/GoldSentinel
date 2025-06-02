from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone

from alert.models.alert_model import AlertModel
from api.serializers.alert_serializer import AlertSerializer
# from permissions.IsResponsableOrAgent import IsResponsableOrAgent # Old permission
from permissions.IsResponsableRegional import IsResponsableRegional # New permission
from permissions.IsAdministrateur import IsAdministrateur # Added for potential broader access later if needed
from permissions.IsAgentAnalyste import IsAgentAnalyste # Added for potential broader access later if needed


class AlertViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsResponsableRegional] # Updated
    """
    ViewSet pour les alertes d'orpaillage
    - GET /api/alerts/ - Liste alertes
    - GET /api/alerts/{id}/ - Détail alerte
    - PUT /api/alerts/{id}/ - Mise à jour alerte
    - PATCH /api/alerts/{id}/status/ - Mise à jour statut
    """
    queryset = AlertModel.objects.all()
    serializer_class = AlertSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['level', 'alert_type', 'alert_status', 'region', 'is_read']
    ordering_fields = ['sent_at', 'level']
    ordering = ['-sent_at']

    # Blocage création manuelle d'alertes
    http_method_names = ['get', 'put', 'patch', 'head', 'options']

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """
        Met à jour le statut d'une alerte
        PATCH /api/alerts/{id}/status/
        Body: {"alert_status": "ACKNOWLEDGED", "assigned_to": user_id}
        """
        try:
            alert = self.get_object()
            new_status = request.data.get('alert_status')
            assigned_to = request.data.get('assigned_to')

            if new_status not in ['ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'FALSE_ALARM']:
                return Response({
                    'error': 'alert_status doit être ACTIVE, ACKNOWLEDGED, RESOLVED ou FALSE_ALARM'
                }, status=status.HTTP_400_BAD_REQUEST)

            alert.alert_status = new_status
            alert.is_read = True

            if assigned_to:
                alert.assigned_to_id = assigned_to

            alert.save()

            serializer = self.get_serializer(alert)
            return Response({
                'message': 'Statut de l\'alerte mis à jour',
                'data': serializer.data
            })

        except Exception as e:
            return Response({
                'error': f'Erreur mise à jour statut: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='active')
    def active_alerts(self, request):
        """
        Alertes actives non lues
        GET /api/alerts/active/
        """
        active_alerts = self.queryset.filter(
            alert_status__in=['ACTIVE', 'ACKNOWLEDGED'],
            is_read=False
        ).order_by('-sent_at')

        serializer = self.get_serializer(active_alerts, many=True)
        return Response({
            'count': active_alerts.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='critical')
    def critical_alerts(self, request):
        """
        Alertes critiques
        GET /api/alerts/critical/
        """
        critical_alerts = self.queryset.filter(
            level__in=['CRITICAL', 'HIGH'],
            alert_status='ACTIVE'
        ).order_by('-sent_at')

        serializer = self.get_serializer(critical_alerts, many=True)
        return Response({
            'count': critical_alerts.count(),
            'results': serializer.data
        })
