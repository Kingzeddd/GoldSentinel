from rest_framework import viewsets, status, permissions # Added permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from gee.services.analysis_orchestrator import AnalysisOrchestrator
from api.serializers.image_serializer import ImageSerializer
from image.models.image_model import ImageModel
from permissions.CanLauchAnalysis import CanLaunchAnalysis


class AnalysisViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, CanLaunchAnalysis] # Updated
    """
    ViewSet pour les analyses d'orpaillage
    - Seul endpoint : POST /api/analysis/run/
    """
    
    @action(detail=False, methods=['post'], url_path='run')
    def run_analysis(self, request):
        """
        Lance une analyse complète de détection d'orpaillage
        POST /api/analysis/run/
        Body: {"months_back": 3}  # Optionnel, défaut: 3 mois
        """
        try:
            print("DEBUG: Début analyse")
            # Paramètres
            months_back = request.data.get('months_back', 3)
            user_id = request.user.id if request.user.is_authenticated else None

            # Validation
            if not isinstance(months_back, int) or months_back < 1 or months_back > 12:
                return Response({
                    'error': 'months_back doit être un entier entre 1 et 12'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Compter les détections AVANT l'analyse
            from detection.models.detection_model import DetectionModel
            detections_before = DetectionModel.objects.count()

            # Lancement analyse
            print("DEBUG: Création orchestrateur")
            orchestrator = AnalysisOrchestrator()
            print("DEBUG: Orchestrateur créé")

            results = orchestrator.run_complete_analysis(months_back, user_id)
            print(f"DEBUG: Résultats = {results}")

            if results['success']:
                # Créer les investigations pour les détections récentes (dernières 2 heures)
                investigations_created = self._create_investigations_for_recent_detections()
                
                return Response({
                    'success': True,
                    'message': 'Analyse terminée avec succès',
                    'data': {
                        'images_processed': results['images_processed'],
                        'detections_found': results['detections_found'],
                        'alerts_generated': results['alerts_generated'],
                        'investigations_created': investigations_created,
                        'analysis_date': timezone.now().isoformat()
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Erreurs lors de l\'analyse',
                    'errors': results['errors']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                'error': f'Erreur inattendue: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_investigations_for_recent_detections(self):
        """
        Crée des investigations pour les détections récentes qui n'en ont pas
        """
        try:
            from detection.models.detection_model import DetectionModel
            from detection.models.investigation_model import InvestigationModel
            
            # Détections des dernières 2 heures sans investigation
            recent_time = timezone.now() - timedelta(hours=2)
            
            # Récupérer les détections récentes qui n'ont pas d'investigation
            recent_detections = DetectionModel.objects.filter(
                detection_date__gte=recent_time
            ).exclude(
                id__in=InvestigationModel.objects.values_list('detection_id', flat=True)
            )
            
            investigations_created = 0
            
            for detection in recent_detections:
                try:
                    # Préparer les données de base
                    investigation_data = {
                        'detection': detection,
                        'status': 'PENDING'
                    }
                    
                    # Ajouter les champs optionnels s'ils existent
                    if self._model_has_field(InvestigationModel, 'priority'):
                        investigation_data['priority'] = self._determine_priority(detection)
                    
                    if self._model_has_field(InvestigationModel, 'created_by'):
                        investigation_data['created_by_id'] = 1  # ID utilisateur système
                    
                    # Créer l'investigation
                    investigation = InvestigationModel.objects.create(**investigation_data)
                    investigations_created += 1
                    print(f"Investigation créée pour détection {detection.id}")
                    
                except Exception as e:
                    print(f"Erreur création investigation pour détection {detection.id}: {e}")
                    continue
            
            print(f"Total investigations créées: {investigations_created}")
            return investigations_created
            
        except Exception as e:
            print(f"Erreur création investigations: {e}")
            return 0
    
    def _model_has_field(self, model, field_name):
        """
        Vérifie si un modèle a un champ spécifique
        """
        try:
            model._meta.get_field(field_name)
            return True
        except:
            return False

    def _determine_priority(self, detection):
        """
        Détermine la priorité de l'investigation basée sur la détection
        """
        try:
            if hasattr(detection, 'confidence_score') and detection.confidence_score:
                if detection.confidence_score >= 0.8:
                    return 'HIGH'
                elif detection.confidence_score >= 0.6:
                    return 'MEDIUM'
                else:
                    return 'LOW'
        except:
            pass
        
        return 'MEDIUM'  # Valeur par défaut