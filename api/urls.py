from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Import tous les viewsets
from api.viewsets.analysis_viewsets import AnalysisViewSet
from api.viewsets.image_viewsets import ImageViewSet
from api.viewsets.detection_viewsets import DetectionViewSet
from api.viewsets.alert_viewsets import AlertViewSet
from api.viewsets.financial_risk_viewsets import FinancialRiskViewSet
from api.viewsets.investigation_viewsets import InvestigationViewSet
from api.viewsets.detection_feedback_viewsets import DetectionFeedbackViewSet
from api.viewsets.event_log_viewsets import EventLogViewSet
from api.viewsets.statistics_viewsets import StatisticsViewSet
from api.viewsets.account_viewsets import AccountViewSet
from api.viewsets.spectral_viewsets import SpectralViewSet
from .viewsets.report_viewsets import ReportViewSet # Import ReportViewSet

# Configuration du router
router = DefaultRouter()


# APIs métier - Endpoints directs
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'images', ImageViewSet, basename='images')
router.register(r'detections', DetectionViewSet, basename='detections')
router.register(r'alerts', AlertViewSet, basename='alerts')
router.register(r'financial-risks', FinancialRiskViewSet, basename='financial-risks')
router.register(r'investigations', InvestigationViewSet, basename='investigations')
router.register(r'feedbacks', DetectionFeedbackViewSet, basename='feedbacks')
router.register(r'events', EventLogViewSet, basename='events')
router.register(r'stats', StatisticsViewSet, basename='stats')
router.register(r'account', AccountViewSet, basename='account')
router.register(r'spectral', SpectralViewSet, basename='spectral')
router.register(r'reports', ReportViewSet, basename='report') # Register ReportViewSet

urlpatterns = [
    # Router principal
    path('', include(router.urls)),

    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]