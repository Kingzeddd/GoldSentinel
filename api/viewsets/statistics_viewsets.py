from rest_framework import viewsets, permissions # Added permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone

from detection.models.detection_model import DetectionModel
from alert.models.alert_model import AlertModel
from alert.models.financial_risk_model import FinancialRiskModel
from detection.models.investigation_model import InvestigationModel
from detection.models.detection_feedback_model import DetectionFeedbackModel
from image.models.image_model import ImageModel
from api.serializers.dashboard_stats_serializer import DashboardStatsSerializer
from report.models.dashboard_statistic_model import DashboardStatistic # Import DashboardStatistic

from permissions.CanViewStats import CanViewStats
class StatisticsViewSet(viewsets.GenericViewSet):

    permission_classes = [permissions.IsAuthenticated, CanViewStats] # Updated
    """
    ViewSet pour les statistiques système
    - GET /api/v1/stats/dashboard/ - Dashboard principal
    - GET /api/v1/stats/summary/ - Résumé exécutif
    - GET /api/v1/stats/detection-trends/ - Tendances détections
    - GET /api/v1/stats/financial-impact/ - Impact financier
    """


    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard_stats(self, request):
        """Statistiques complètes pour dashboard"""
        try:
            today = timezone.now().date()
            latest_stats = DashboardStatistic.objects.filter(
                region__isnull=True, # Global stats
                date_calculated=today
            ).order_by('-updated_at') # Should be unique per day, but just in case

            precalculated_data = {}
            for stat_entry in latest_stats:
                precalculated_data[stat_entry.statistic_type] = stat_entry.value

            # Période d'analyse (still used for some on-the-fly calculations)
            thirty_days_ago = timezone.now() - timedelta(days=30)

            # Compteurs principaux - try precalculated first, then fallback
            total_detections = precalculated_data.get(
                DashboardStatistic.StatisticTypeChoices.TOTAL_DETECTIONS.value,
                DetectionModel.objects.count() # Fallback
            )
            active_alerts = precalculated_data.get(
                DashboardStatistic.StatisticTypeChoices.ACTIVE_ALERTS.value,
                AlertModel.objects.filter(alert_status=AlertModel.AlertStatusChoices.ACTIVE).count() # Fallback
            )

            # These remain on-the-fly for now
            pending_investigations = InvestigationModel.objects.filter(status=InvestigationModel.StatusChoices.PENDING).count()

            # Risque financier total (remains on-the-fly)
            total_risk = FinancialRiskModel.objects.aggregate(
                total=Sum('estimated_loss')
            )['total'] or 0

            # Dernière analyse
            last_image = ImageModel.objects.filter(
                processing_status='COMPLETED'
            ).order_by('-processed_at').first()

            # Précision système
            feedback_stats = self._calculate_accuracy()

            # Tendances détections (7 derniers jours)
            trends = self._get_detection_trends()

            # Alertes par niveau
            alerts_by_level = dict(AlertModel.objects.values('level').annotate(count=Count('id')))

            # Zones affectées
            affected_zones = self._get_affected_zones()

            stats_data = {
                'total_detections': total_detections,
                'active_alerts': active_alerts,
                'pending_investigations': pending_investigations,
                'total_financial_risk': total_risk,
                'analysis_period_days': 30,
                'last_analysis_date': last_image.processed_at if last_image else None,
                'accuracy_rate': feedback_stats['accuracy'],
                'high_confidence_detections': DetectionModel.objects.filter(confidence_score__gte=0.7).count(),
                'detections_trend': trends,
                'alerts_by_level': alerts_by_level,
                'affected_zones': affected_zones
            }

            serializer = DashboardStatsSerializer(stats_data)
            return Response(serializer.data)

        except Exception as e:
            return Response({
                'error': f'Erreur calcul statistiques: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['get'], url_path='summary')
    def executive_summary(self, request):
        """Résumé exécutif pour direction"""
        try:
            # Métriques clés
            total_detections = DetectionModel.objects.count()
            critical_alerts = AlertModel.objects.filter(level='CRITICAL').count()
            total_financial_impact = FinancialRiskModel.objects.aggregate(Sum('estimated_loss'))['total'] or 0

            # Efficacité système
            feedback_count = DetectionFeedbackModel.objects.count()
            confirmed_detections = DetectionFeedbackModel.objects.filter(ground_truth_confirmed=True).count()
            accuracy = (confirmed_detections / feedback_count * 100) if feedback_count > 0 else 0

            # Investigations en cours
            active_investigations = InvestigationModel.objects.filter(
                status__in=['ASSIGNED', 'IN_PROGRESS']
            ).count()

            return Response({
                'period': 'Depuis le début du système',
                'key_metrics': {
                    'total_detections': total_detections,
                    'critical_situations': critical_alerts,
                    'estimated_financial_impact_fcfa': total_financial_impact,
                    'system_accuracy_percent': round(accuracy, 1),
                    'active_field_investigations': active_investigations
                },
                'recommendations': self._get_executive_recommendations(accuracy, critical_alerts),
                'next_actions': [
                    'Poursuivre monitoring automatique',
                    'Finaliser investigations en cours',
                    'Étendre couverture géographique' if accuracy > 80 else 'Améliorer précision algorithmes'
                ]
            })

        except Exception as e:
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['get'], url_path='detection-trends')
    def detection_trends(self, request):
        """Tendances de détection sur période"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        # Détections par jour
        daily_detections = (DetectionModel.objects
                            .filter(detection_date__gte=start_date)
                            .extra({'day': "date(detection_date)"})
                            .values('day')
                            .annotate(count=Count('id'))
                            .order_by('day'))

        # Évolution scores de confiance
        confidence_evolution = (DetectionModel.objects
        .filter(detection_date__gte=start_date)
        .aggregate(
            avg_confidence=Avg('confidence_score'),
            high_confidence_count=Count('id', filter=Q(confidence_score__gte=0.7))
        ))

        return Response({
            'period_days': days,
            'daily_detections': list(daily_detections),
            'average_confidence': confidence_evolution['avg_confidence'],
            'high_confidence_count': confidence_evolution['high_confidence_count'],
            'trend_analysis': self._analyze_trend(daily_detections)
        })

    @action(detail=False, methods=['get'], url_path='financial-impact')
    def financial_impact(self, request):
        """Analyse impact financier détaillé"""
        # Impact par niveau de risque
        risk_breakdown = (FinancialRiskModel.objects
        .values('risk_level')
        .annotate(
            count=Count('id'),
            total_amount=Sum('estimated_loss'),
            avg_amount=Avg('estimated_loss')
        ))

        # Impact par hectare moyen
        area_impact = FinancialRiskModel.objects.aggregate(
            total_area=Sum('area_hectares'),
            total_loss=Sum('estimated_loss')
        )

        cost_per_hectare = 0
        if area_impact['total_area'] and area_impact['total_area'] > 0:
            cost_per_hectare = area_impact['total_loss'] / area_impact['total_area']

        return Response({
            'total_estimated_loss_fcfa': area_impact['total_loss'] or 0,
            'total_affected_area_hectares': area_impact['total_area'] or 0,
            'average_cost_per_hectare_fcfa': round(cost_per_hectare, 0),
            'breakdown_by_risk_level': list(risk_breakdown),
            'economic_context': {
                'ministry_annual_estimate_fcfa': 3_000_000_000_000,  # 3000 milliards
                'our_detection_percentage': self._calculate_detection_coverage(area_impact['total_loss'] or 0)
            }
        })

    def _calculate_accuracy(self):
        """Calcule précision système"""
        total_feedback = DetectionFeedbackModel.objects.count()
        if total_feedback == 0:
            return {'accuracy': 0, 'sample_size': 0}

        confirmed = DetectionFeedbackModel.objects.filter(ground_truth_confirmed=True).count()
        return {
            'accuracy': round((confirmed / total_feedback) * 100, 1),
            'sample_size': total_feedback
        }

    def _get_detection_trends(self):
        """Tendances détections 7 jours"""
        trends = []
        for i in range(7):
            date = timezone.now().date() - timedelta(days=i)
            count = DetectionModel.objects.filter(detection_date__date=date).count()
            trends.append({'date': date.isoformat(), 'count': count})
        return trends[::-1]  # Ordre chronologique

    def _get_affected_zones(self):
        """Zones les plus affectées"""
        zones = (DetectionModel.objects
                 .values('region__name')
                 .annotate(count=Count('id'))
                 .order_by('-count')[:5])
        return [{'zone': z['region__name'], 'detections': z['count']} for z in zones]

    def _get_executive_recommendations(self, accuracy, critical_alerts):
        """Recommandations pour direction"""
        recommendations = []

        if accuracy > 85:
            recommendations.append("Système très performant - Étendre à d'autres régions")
        elif accuracy > 70:
            recommendations.append("Performance correcte - Continuer amélioration continue")
        else:
            recommendations.append("Précision insuffisante - Réviser algorithmes de détection")

        if critical_alerts > 5:
            recommendations.append("Situation critique - Mobiliser équipes terrain d'urgence")

        return recommendations

    def _analyze_trend(self, daily_data):
        """Analyse tendance croissante/décroissante"""
        if len(daily_data) < 2:
            return "Données insuffisantes"

        # Ensure there are enough data points for averaging
        recent_slice = daily_data[-3:]
        older_slice = daily_data[:3]

        if not recent_slice or not older_slice:
            return "Données insuffisantes pour une analyse de tendance significative."

        recent_avg = sum(d['count'] for d in recent_slice) / len(recent_slice)
        older_avg = sum(d['count'] for d in older_slice) / len(older_slice)


        if recent_avg > older_avg * 1.2:
            return "Tendance croissante"
        elif recent_avg < older_avg * 0.8:
            return "Tendance décroissante"
        else:
            return "Stable"

    def _calculate_detection_coverage(self, our_total_loss):
        """Calcule % couverture par rapport estimation ministère"""
        ministry_estimate = 3_000_000_000_000  # 3000 milliards
        if our_total_loss > 0 and ministry_estimate > 0: # ensure ministry_estimate is not zero
            return round((our_total_loss / ministry_estimate) * 100, 3)
        return 0
