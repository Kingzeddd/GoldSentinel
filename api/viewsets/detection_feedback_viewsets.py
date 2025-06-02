from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from permissions.IsResponsableRegional import IsResponsableRegional
from detection.models.detection_feedback_model import DetectionFeedbackModel
from api.serializers.detection_feedback_serializer import DetectionFeedbackSerializer


class DetectionFeedbackViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsResponsableRegional]
    """
    ViewSet pour les feedbacks de détection (lecture seule)
    - GET /api/v1/feedbacks/ - Liste feedbacks
    - GET /api/v1/feedbacks/training-data/ - Données d'entraînement
    - GET /api/v1/feedbacks/accuracy-stats/ - Statistiques précision
    """
    queryset = DetectionFeedbackModel.objects.all()
    serializer_class = DetectionFeedbackSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ground_truth_confirmed', 'used_for_training']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'], url_path='training-data')
    def training_data(self, request):
        """
        Feedbacks prêts pour l'entraînement
        GET /api/v1/feedbacks/training-data/
        """
        training_feedbacks = self.queryset.filter(used_for_training=False)
        serializer = self.get_serializer(training_feedbacks, many=True)

        return Response({
            'count': training_feedbacks.count(),
            'confirmed_count': training_feedbacks.filter(ground_truth_confirmed=True).count(),
            'false_positive_count': training_feedbacks.filter(ground_truth_confirmed=False).count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='accuracy-stats')
    def accuracy_statistics(self, request):
        """
        Statistiques de précision du système
        GET /api/v1/feedbacks/accuracy-stats/
        """
        total_feedbacks = self.queryset.count()

        if total_feedbacks == 0:
            return Response({
                'message': 'Aucun feedback disponible',
                'stats': None
            })

        confirmed = self.queryset.filter(ground_truth_confirmed=True).count()
        false_positives = self.queryset.filter(ground_truth_confirmed=False).count()

        accuracy = (confirmed / total_feedbacks) * 100

        # Analyse par niveau de confiance
        high_confidence = self.queryset.filter(original_confidence__gte=0.8)
        high_conf_accuracy = 0
        if high_confidence.count() > 0:
            high_conf_confirmed = high_confidence.filter(ground_truth_confirmed=True).count()
            high_conf_accuracy = (high_conf_confirmed / high_confidence.count()) * 100

        return Response({
            'total_evaluations': total_feedbacks,
            'confirmed_detections': confirmed,
            'false_positives': false_positives,
            'overall_accuracy': round(accuracy, 2),
            'high_confidence_accuracy': round(high_conf_accuracy, 2),
            'recommendations': self._get_recommendations(accuracy, high_conf_accuracy)
        })

    def _get_recommendations(self, overall_accuracy, high_conf_accuracy):
        """Recommandations basées sur les statistiques"""
        recommendations = []

        if overall_accuracy < 70:
            recommendations.append("Précision globale faible - Ajuster les seuils de détection")

        if high_conf_accuracy > 90:
            recommendations.append("Haute confiance fiable - Automatiser les détections > 0.8")

        if overall_accuracy > 85:
            recommendations.append("Système performant - Prêt pour déploiement étendu")

        return recommendations
