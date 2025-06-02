from rest_framework import viewsets, permissions # Added permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from alert.models.financial_risk_model import FinancialRiskModel
from api.serializers.financial_risk_serializer import FinancialRiskSerializer
# from permissions.CanViewStats import CanViewStats # Old permission
from permissions.IsResponsableRegional import IsResponsableRegional # New permission

class FinancialRiskViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsResponsableRegional] # Updated
    """
    ViewSet pour les risques financiers
    - GET /api/financial-risks/ - Liste risques
    - GET /api/financial-risks/{id}/ - Détail risque
    """
    queryset = FinancialRiskModel.objects.all()
    serializer_class = FinancialRiskSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['risk_level']
    ordering_fields = ['estimated_loss', 'area_hectares', 'created_at']
    ordering = ['-estimated_loss']

    @action(detail=False, methods=['get'], url_path='high-impact')
    def high_impact_risks(self, request):
        """
        Risques financiers élevés (>= 500k FCFA)
        GET /api/financial-risks/high-impact/
        """
        high_risks = self.queryset.filter(
            estimated_loss__gte=500000
        ).order_by('-estimated_loss')

        serializer = self.get_serializer(high_risks, many=True)

        total_loss = sum(risk.estimated_loss for risk in high_risks)

        return Response({
            'count': high_risks.count(),
            'total_estimated_loss': total_loss,
            'results': serializer.data
        })
