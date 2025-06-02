# api/viewsets/report_viewsets.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend # For filtering

from report.models import ReportModel # Assuming exposed in report/models/__init__.py
from ..serializers.report_serializer import ReportSerializer # Relative import for serializer
from report.tasks import generate_report_task # Assuming exposed in report/__init__.py or report/tasks.py is findable

# Import permissions (specific ones can be added later if default behavior is not enough)
# from permissions.IsAdministrateur import IsAdministrateur
# from permissions.IsResponsableRegional import IsResponsableRegional

class ReportViewSet(viewsets.ModelViewSet):
    queryset = ReportModel.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    # Note: For ForeignKey fields like 'region' and 'generated_by', filtering by ID is default.
    # To filter by name (e.g., region__name), you'd define that in a custom FilterSet class.
    filterset_fields = ['report_type', 'status', 'region', 'file_format', 'generated_by']

    # Allow POST for the 'generate-report' action, GET for list/retrieve, DELETE for cleanup.
    # PUT/PATCH are also included by default in ModelViewSet but might need specific permission handling
    # if direct modification of ReportModel instances (outside of task updates) is allowed.
    http_method_names = ['get', 'post', 'delete', 'head', 'options'] # Removed 'put', 'patch' for now to make it more controlled

    def get_queryset(self):
        """
        Filters reports based on user role:
        - Superusers/Admins/Responsables Régionaux see all reports.
        - Other authenticated users see only reports they generated.
        """
        user = self.request.user
        if user.is_superuser or \
           user.user_authorities.filter(authority__name__in=['Administrateur', 'Responsable Régional']).exists():
            # Admins and Responsables Régionaux can see all reports.
            # TODO: Future refinement: Responsable Régional could be limited to reports for their region(s).
            return ReportModel.objects.all().order_by('-created_at')

        # Default for other authenticated users: only see reports they generated.
        return ReportModel.objects.filter(generated_by=user).order_by('-created_at')

    @action(detail=False, methods=['post'], url_path='generate-report')
    def generate_report(self, request):
        """
        Action to trigger asynchronous report generation.
        Required in request.data: 'name' (str) and 'report_type' (str - one of ReportModel.ReportTypeChoices).
        Optional in request.data: 'region_id' (int), 'start_date' (str YYYY-MM-DD),
                                 'end_date' (str YYYY-MM-DD), 'summary' (str),
                                 'external_url' (str), 'file_format' (str - one of ReportModel.FileFormatChoices).
        """
        report_type = request.data.get('report_type')
        name = request.data.get('name')

        if not name:
            return Response({'error': "'name' for the report is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not report_type:
            return Response({'error': "'report_type' is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate report_type
        valid_report_types = [choice[0] for choice in ReportModel.ReportTypeChoices.choices]
        if report_type not in valid_report_types:
            return Response({'error': f"Invalid 'report_type'. Valid options are: {valid_report_types}"}, status=status.HTTP_400_BAD_REQUEST)

        file_format_request = request.data.get('file_format', ReportModel.FileFormatChoices.CSV)
        valid_file_formats = [choice[0] for choice in ReportModel.FileFormatChoices.choices]
        if file_format_request not in valid_file_formats:
             return Response({'error': f"Invalid 'file_format'. Valid options are: {valid_file_formats}"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data for ReportModel creation
        # Note: generated_by is set automatically by the serializer if CreateReportSerializer is used
        # or needs to be explicitly passed if using ReportSerializer directly for creation.
        # For this action, we are explicitly setting it.

        # Basic validation for dates if provided
        start_date_val = request.data.get('start_date')
        end_date_val = request.data.get('end_date')
        if start_date_val and end_date_val and start_date_val > end_date_val:
            return Response({'error': "start_date cannot be after end_date."}, status=status.HTTP_400_BAD_REQUEST)

        # Data for the serializer. We will set 'generated_by' and 'status' manually.
        serializer_data = {
            'name': name,
            'report_type': report_type,
            'file_format': file_format_request,
            'region': request.data.get('region_id'), # Serializer will handle FK
            'start_date': start_date_val,
            'end_date': end_date_val,
            'summary': request.data.get('summary', ''),
            'external_url': request.data.get('external_url')
        }

        # Use ReportSerializer for validation and creation
        # We need to add 'generated_by' to the context or pass it directly if serializer is not set up for it
        serializer = self.get_serializer(data=serializer_data)
        if serializer.is_valid():
            # Manually set fields not typically part of user input for creation
            report_instance = serializer.save(
                generated_by=request.user,
                status=ReportModel.StatusChoices.PENDING
            )

            # Dispatch Celery task
            generate_report_task.delay(report_instance.id, request.user.id)

            # Return the serialized data of the created report instance (now with PENDING status)
            # We need to re-serialize the instance to get all fields, including read-only ones.
            response_serializer = self.get_serializer(report_instance)
            return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Standard ModelViewSet actions (list, retrieve, destroy) are inherited.
    # `destroy` will use the default IsAuthenticated permission.
    # Object-level permissions for `destroy` (e.g., only owner or admin) can be added by overriding the method.
    # The get_queryset method already limits non-admin/non-responsable to their own reports,
    # so they can only delete their own reports if http_method_names includes 'delete'.
    # Admins/Responsables can delete any based on get_queryset returning all.

    # If specific roles for deletion are needed beyond ownership or superuser:
    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if not (request.user == instance.generated_by or IsAdministrateur().has_object_permission(request, self, instance)):
    #         self.permission_denied(request, message="You do not have permission to delete this report.")
    #     return super().destroy(request, *args, **kwargs)
