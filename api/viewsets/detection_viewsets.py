from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from detection.models.detection_model import DetectionModel
from api.serializers.detection_serializer import DetectionSerializer

from permissions.IsResponsableRegional import IsResponsableRegional
class DetectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsResponsableRegional]
    """
    ViewSet pour les détections d'orpaillage
    - GET /api/detections/ - Liste détections
    - GET /api/detections/{id}/ - Détail détection
    - PUT /api/detections/{id}/ - Mise à jour détection (validation)
    - DELETE /api/detections/{id}/ - Supprimer (faux positif)
    """
    queryset = DetectionModel.objects.all()
    serializer_class = DetectionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['detection_type', 'validation_status', 'region']
    ordering_fields = ['confidence_score', 'detection_date', 'area_hectares']
    ordering = ['-detection_date']

    # Blocage des méthodes non désirées
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options']

    @action(detail=True, methods=['patch'], url_path='validate')
    def validate_detection(self, request, pk=None):
        """
        Valide une détection
        PATCH /api/detections/{id}/validate/
        Body: {"validation_status": "VALIDATED", "validated_by": user_id}
        """
        try:
            detection = self.get_object()
            validation_status = request.data.get('validation_status')

            if validation_status not in ['VALIDATED', 'FALSE_POSITIVE', 'CONFIRMED']:
                return Response({
                    'error': 'validation_status doit être VALIDATED, FALSE_POSITIVE ou CONFIRMED'
                }, status=status.HTTP_400_BAD_REQUEST)

            detection.validation_status = validation_status
            detection.validated_by = request.user if request.user.is_authenticated else None
            detection.validated_at = timezone.now()
            detection.save()

            serializer = self.get_serializer(detection)
            return Response({
                'message': 'Détection validée avec succès',
                'data': serializer.data
            })

        except Exception as e:
            return Response({
                'error': f'Erreur validation: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='high-confidence')
    def high_confidence_detections(self, request):
        """
        Détections avec score de confiance élevé (>= 0.7)
        GET /api/detections/high-confidence/
        """
        high_conf_detections = self.queryset.filter(
            confidence_score__gte=0.7,
            validation_status='DETECTED'
        ).order_by('-confidence_score')

        serializer = self.get_serializer(high_conf_detections, many=True)
        return Response({
            'count': high_conf_detections.count(),
            'results': serializer.data
        })
