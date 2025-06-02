from rest_framework import viewsets, permissions # Updated import
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
# from rest_framework.permissions import IsAuthenticated # Old specific import
from image.models.image_model import ImageModel
from api.serializers.image_serializer import ImageSerializer
from permissions.IsAgentTechnique import IsAgentTechnique # New permission


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAgentTechnique] # Updated
    """
    ViewSet pour les images satellites
    - GET /api/images/ - Liste images
    - GET /api/images/{id}/ - Détail image
    """
    queryset = ImageModel.objects.all()
    serializer_class = ImageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['satellite_source', 'processing_status', 'region']
    ordering_fields = ['capture_date', 'processed_at', 'created_at']
    ordering = ['-capture_date']

    @action(detail=False, methods=['get'], url_path='recent')
    def recent_images(self, request):
        """
        Récupère les images récentes (30 derniers jours)
        GET /api/images/recent/
        """
        from datetime import datetime, timedelta

        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_images = self.queryset.filter(
            capture_date__gte=thirty_days_ago,
            processing_status='COMPLETED'
        ).order_by('-capture_date')

        serializer = self.get_serializer(recent_images, many=True)
        return Response({
            'count': recent_images.count(),
            'results': serializer.data
        })
