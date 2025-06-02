from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from image.models.image_model import ImageModel
from gee.services.earth_engine_service import EarthEngineService
from permissions.CanLauchAnalysis import CanLaunchAnalysis


class SpectralViewSet(viewsets.ViewSet):
    """ViewSet pour les cartes d'indices spectraux"""
    permission_classes = [IsAuthenticated, CanLaunchAnalysis]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gee_service = EarthEngineService()

    @action(detail=False, methods=['get'], url_path='maps/(?P<image_id>[^/.]+)')
    def get_spectral_maps(self, request, image_id=None):
        """
        Récupère les cartes d'indices spectraux pour une image
        """
        try:
            # Récupération image
            image = ImageModel.objects.get(id=image_id)
            
            if not image.gee_asset_id:
                return Response(
                    {'error': 'Image sans asset Google Earth Engine'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Génération cartes spectrales
            maps_data = self.gee_service.generate_spectral_maps(image.gee_asset_id)
            
            if not maps_data:
                return Response(
                    {'error': 'Erreur génération cartes spectrales'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Ajout métadonnées image
            response_data = {
                'image_id': image.id,
                'image_name': image.name,
                'capture_date': image.capture_date,
                'region': image.region.name,
                'spectral_maps': maps_data,
                'indices_data': {
                    'ndvi': image.ndvi_data,
                    'ndwi': image.ndwi_data,
                    'ndti': image.ndti_data
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ImageModel.DoesNotExist:
            return Response(
                {'error': 'Image non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='indices/(?P<image_id>[^/.]+)')
    def get_indices_data(self, request, image_id=None):
        """
        Récupère uniquement les données d'indices spectraux
        """
        try:
            image = ImageModel.objects.get(id=image_id)
            
            indices_data = {
                'image_id': image.id,
                'ndvi_data': image.ndvi_data,
                'ndwi_data': image.ndwi_data,
                'ndti_data': image.ndti_data,
                'ndvi_mean': image.ndvi_mean,
                'ndwi_mean': image.ndwi_mean,
                'ndti_mean': image.ndti_mean,
                'processing_status': image.processing_status,
                'processed_at': image.processed_at
            }

            return Response(indices_data, status=status.HTTP_200_OK)

        except ImageModel.DoesNotExist:
            return Response(
                {'error': 'Image non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='trends/(?P<region_id>[^/.]+)')
    def get_indices_trends(self, request, region_id=None):
        """
        Récupère l'évolution temporelle des indices pour une région
        """
        try:
            # Récupération images de la région (30 derniers jours)
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
            images = ImageModel.objects.filter(
                region_id=region_id,
                processing_status='COMPLETED',
                capture_date__gte=start_date,
                capture_date__lte=end_date
            ).order_by('capture_date')

            trends_data = []
            for image in images:
                trends_data.append({
                    'date': image.capture_date.isoformat(),
                    'ndvi_mean': image.ndvi_mean,
                    'ndwi_mean': image.ndwi_mean,
                    'ndti_mean': image.ndti_mean,
                    'image_id': image.id
                })

            return Response({
                'region_id': region_id,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'trends': trends_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Erreur serveur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
