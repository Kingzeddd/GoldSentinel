from rest_framework import viewsets, status, permissions # Added permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from detection.models.investigation_model import InvestigationModel
from detection.models.detection_feedback_model import DetectionFeedbackModel
from api.serializers.investigation_serializer import InvestigationSerializer
from permissions.CanManageInvestigations import CanManageInvestigations
from permissions.IsAgentTerrain import IsAgentTerrain # Import IsAgentTerrain

User = get_user_model()


class InvestigationViewSet(viewsets.ModelViewSet):
    # Default permission_classes, will be overridden by get_permissions
    permission_classes = [permissions.IsAuthenticated, CanManageInvestigations]
    queryset = InvestigationModel.objects.all()
    serializer_class = InvestigationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'result', 'assigned_to']
    ordering_fields = ['created_at', 'investigation_date']
    ordering = ['-created_at']
    # Ensure 'put', 'patch' are in http_method_names if update/partial_update are to be used.
    # 'post' for create, 'delete' for destroy. Default ModelViewSet includes all.
    # The current list ['get', 'put', 'patch', 'head', 'options'] disables create and delete.
    # Let's assume this is intentional or will be handled separately.
    http_method_names = ['get', 'put', 'patch', 'head', 'options', 'delete'] # Added delete for completeness, assuming create is not for this view directly

    def get_permissions(self):
        if self.action == 'my_investigations':
            self.permission_classes = [permissions.IsAuthenticated, IsAgentTerrain]
        elif self.action == 'submit_result':
            # Object-level check will be done in the action method
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            # Object-level check will be done in the overridden methods
            self.permission_classes = [permissions.IsAuthenticated]
        # Create, List, Retrieve, Assign, Available Agents, Pending Investigations use default
        elif self.action in ['create', 'assign_investigation', 'available_agents', 'pending_investigations', 'list', 'retrieve', 'destroy']:
             self.permission_classes = [permissions.IsAuthenticated, CanManageInvestigations]
        else: # Default for any other custom actions not listed
            self.permission_classes = [permissions.IsAuthenticated, CanManageInvestigations]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        investigation = self.get_object()
        is_assigned_agent = (request.user == investigation.assigned_to)
        # Check general permission using an instance of CanManageInvestigations
        can_manage_globally = CanManageInvestigations().has_permission(request, self)

        if not (is_assigned_agent or can_manage_globally):
            self.permission_denied(
                request, message="You can only update investigations assigned to you or if you have management permissions."
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        investigation = self.get_object()
        is_assigned_agent = (request.user == investigation.assigned_to)
        can_manage_globally = CanManageInvestigations().has_permission(request, self)

        if not (is_assigned_agent or can_manage_globally):
            self.permission_denied(
                request, message="You can only update investigations assigned to you or if you have management permissions."
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_investigations(self, request):
        pending = self.queryset.filter(status='PENDING').order_by('-created_at')
        serializer = self.get_serializer(pending, many=True)
        return Response({
            'count': pending.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def my_investigations(self, request):
        if not request.user.is_authenticated: # This check is redundant due to IsAuthenticated permission class
            return Response({'error': 'Authentification requise'},
                            status=status.HTTP_401_UNAUTHORIZED)

        my_investigations = self.queryset.filter(
            assigned_to=request.user,
            status__in=['ASSIGNED', 'IN_PROGRESS']
        ).order_by('-created_at')

        serializer = self.get_serializer(my_investigations, many=True)
        return Response({
            'count': my_investigations.count(),
            'results': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='available-agents')
    def available_agents(self, request):
        try:
            agents_terrain = User.objects.filter(
                user_authorities__authority__name='Agent Terrain',
                user_authorities__status=True,
                is_active=True
            ).annotate(
                active_investigations=Count(
                    'assigned_investigations',
                    filter=Q(assigned_investigations__status__in=['ASSIGNED', 'IN_PROGRESS'])
                ),
                pending_investigations=Count(
                    'assigned_investigations',
                    filter=Q(assigned_investigations__status='PENDING')
                )
            ).distinct()

            agents_data = []
            for agent in agents_terrain:
                total_workload = agent.active_investigations + agent.pending_investigations

                # Get user identifier - use email or id if username doesn't exist
                user_identifier = getattr(agent, 'username', None) or getattr(agent, 'email', f'user_{agent.id}')

                agent_info = {
                    'id': agent.id,
                    'full_name': f"{agent.first_name} {agent.last_name}".strip(),
                    'identifier': user_identifier,  # Changed from 'username' to 'identifier'
                    'email': agent.email,
                    'active_investigations_count': agent.active_investigations,
                    'pending_investigations_count': agent.pending_investigations,
                    'total_workload': total_workload,
                    'availability_status': self._get_availability_status(total_workload),
                    'last_login': agent.last_login.isoformat() if agent.last_login else None
                }
                agents_data.append(agent_info)

            agents_data.sort(key=lambda x: x['total_workload'])

            return Response({
                'count': len(agents_data),
                'agents': agents_data,
                'summary': {
                    'total_agents': len(agents_data),
                    'available_agents': len([a for a in agents_data if a['availability_status'] == 'DISPONIBLE']),
                    'busy_agents': len([a for a in agents_data if a['availability_status'] == 'OCCUPÉ']),
                    'overloaded_agents': len([a for a in agents_data if a['availability_status'] == 'SURCHARGÉ'])
                }
            })

        except Exception as e:
            return Response({
                'error': f'Erreur récupération agents: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='assign')
    def assign_investigation(self, request, pk=None):
        try:
            investigation = self.get_object()
            assigned_to_id = request.data.get('assigned_to')
            priority = request.data.get('priority', 'MEDIUM')
            assignment_notes = request.data.get('notes', '')

            if not assigned_to_id:
                return Response({
                    'error': 'assigned_to est requis'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                agent = User.objects.get(
                    id=assigned_to_id,
                    user_authorities__authority__name='Agent Terrain',
                    user_authorities__status=True,
                    is_active=True
                )
            except User.DoesNotExist:
                return Response({
                    'error': 'Agent terrain introuvable ou inactif'
                }, status=status.HTTP_400_BAD_REQUEST)

            if investigation.status != 'PENDING':
                return Response({
                    'error': f'Investigation déjà {investigation.status}. Seules les investigations PENDING peuvent être assignées'
                }, status=status.HTTP_400_BAD_REQUEST)

            current_workload = InvestigationModel.objects.filter(
                assigned_to=agent,
                status__in=['ASSIGNED', 'IN_PROGRESS', 'PENDING']
            ).count()

            investigation.assigned_to = agent
            investigation.status = 'ASSIGNED'
            investigation.assigned_at = timezone.now()
            investigation.assigned_by = request.user

            if hasattr(investigation, 'priority'):
                investigation.priority = priority
            if hasattr(investigation, 'assignment_notes'):
                investigation.assignment_notes = assignment_notes

            investigation.save()

            self._log_assignment(investigation, request.user, agent)

            serializer = self.get_serializer(investigation)
            response_data = {
                'success': True,
                'message': f'Investigation assignée à {agent.get_full_name()}',
                'data': serializer.data,
                'agent_info': {
                    'name': agent.get_full_name(),
                    'new_workload': current_workload + 1
                }
            }

            if current_workload >= 8:
                response_data[
                    'warning'] = f'Attention: {agent.get_full_name()} a maintenant {current_workload + 1} investigations'

            return Response(response_data)

        except Exception as e:
            return Response({
                'error': f'Erreur assignation: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='result')
    def submit_result(self, request, pk=None):
        try:
            investigation = self.get_object()

            # Permission Check
            is_assigned_agent = (request.user == investigation.assigned_to)
            can_manage_globally = CanManageInvestigations().has_permission(request, self)

            if not (is_assigned_agent or can_manage_globally):
                return Response({'error': 'You can only submit results for investigations assigned to you or if you have management permissions.'}, status=status.HTTP_403_FORBIDDEN)

            if investigation.status not in [InvestigationModel.StatusChoices.ASSIGNED, InvestigationModel.StatusChoices.IN_PROGRESS]:
                 return Response({'error': f'Cannot submit result for investigation with status {investigation.status}. Must be ASSIGNED or IN_PROGRESS.'}, status=status.HTTP_400_BAD_REQUEST)

            result = request.data.get('result')
            field_notes = request.data.get('field_notes', '')
            investigation_date = request.data.get('investigation_date')

            if result not in [InvestigationModel.ResultChoices.CONFIRMED, InvestigationModel.ResultChoices.FALSE_POSITIVE, InvestigationModel.ResultChoices.NEEDS_MONITORING]:
                return Response({
                    'error': f"result doit être l'un de {', '.join([r[0] for r in InvestigationModel.ResultChoices.choices])}"
                }, status=status.HTTP_400_BAD_REQUEST)

            investigation.result = result
            investigation.field_notes = field_notes
            investigation.status = InvestigationModel.StatusChoices.COMPLETED

            if investigation_date:
                from datetime import datetime
                investigation.investigation_date = datetime.strptime(investigation_date, '%Y-%m-%d').date()
            else:
                investigation.investigation_date = timezone.now().date()

            investigation.save()
            self._create_detection_feedback(investigation)

            serializer = self.get_serializer(investigation)
            return Response({
                'message': 'Résultat investigation enregistré',
                'data': serializer.data
            })

        except Exception as e:
            return Response({
                'error': f'Erreur soumission résultat: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_availability_status(self, total_workload):
        if total_workload == 0:
            return 'DISPONIBLE'
        elif total_workload <= 3:
            return 'DISPONIBLE'
        elif total_workload <= 7:
            return 'OCCUPÉ'
        else:
            return 'SURCHARGÉ'

    def _log_assignment(self, investigation, assigned_by, assigned_to):
        try:
            from report.models.event_log_model import EventLogModel
            EventLogModel.objects.create(
                event_type='INVESTIGATION_ASSIGNED',
                description=f'Investigation {investigation.id} assignée à {assigned_to.get_full_name()}',
                user=assigned_by,
                region=investigation.detection.region if investigation.detection else None,
                metadata={
                    'investigation_id': investigation.id,
                    'assigned_to_id': assigned_to.id,
                    'assigned_to_name': assigned_to.get_full_name()
                }
            )
        except Exception as e:
            print(f"Erreur logging assignation: {e}")

    def _create_detection_feedback(self, investigation):
        try:
            detection = investigation.detection
            DetectionFeedbackModel.objects.create(
                detection=detection,
                investigation=investigation,
                original_confidence=detection.confidence_score,
                original_ndvi_score=detection.ndvi_anomaly_score or 0,
                original_ndwi_score=detection.ndwi_anomaly_score or 0,
                original_ndti_score=detection.ndti_anomaly_score or 0,
                ground_truth_confirmed=(investigation.result == 'CONFIRMED'),
                agent_confidence=2, # Placeholder, consider how to capture this
                used_for_training=False
            )
            print(f"Feedback créé pour détection {detection.id}")
        except Exception as e:
            print(f"Erreur création feedback: {e}")