# api/serializers/report_serializer.py
from rest_framework import serializers
from report.models import ReportModel # Assuming ReportModel is in report/models/__init__.py or directly accessible
from account.models.user_model import UserModel # Corrected path based on previous fixes
from region.models.region_model import RegionModel # Corrected path

class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.SerializerMethodField(read_only=True)
    region_name = serializers.SerializerMethodField(read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    file_format_display = serializers.CharField(source='get_file_format_display', read_only=True)

    # Make report_file accessible for download links
    # Using FileField to get the URL automatically if configured, or just the path.
    report_file_url = serializers.FileField(source='report_file', read_only=True, use_url=True)


    class Meta:
        model = ReportModel
        fields = [
            'id', 'name',
            'report_type', 'report_type_display',
            'status', 'status_display',
            'file_format', 'file_format_display',
            'generated_by', 'generated_by_name',
            'region', 'region_name',
            'start_date', 'end_date',
            'summary', 'report_file_url', 'external_url',
            'processing_error_message',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id',
            # 'status' should be read-only as it's managed by the generation task
            'status', 'status_display',
            # 'file_format' is set on creation, 'file_format_display' is derived
            'file_format_display',
            'generated_by_name',
            'region_name',
            'report_file_url',
            'processing_error_message',
            'created_at', 'updated_at',
            'report_type_display',
        ]
        # Fields that can be provided during creation via an API endpoint:
        # 'name', 'report_type', 'file_format' (this could be a choice for generation)
        # 'region' (optional FK), 'start_date' (optional), 'end_date' (optional),
        # 'summary' (optional), 'external_url' (optional)
        # 'generated_by' will be set to request.user by the view.
        # 'status' will be set to PENDING by default or by the view.

    def get_generated_by_name(self, obj):
        return obj.generated_by.get_full_name() if obj.generated_by else None

    def get_region_name(self, obj):
        return obj.region.name if obj.region else None

    def to_representation(self, instance):
        """Modify representation to use URL for report_file if available."""
        representation = super().to_representation(instance)
        if instance.report_file and hasattr(instance.report_file, 'url'):
            representation['report_file_url'] = instance.report_file.url
        else:
            # If no file or no URL (e.g. file not uploaded to media storage properly),
            # set to None or keep the string path based on DRF default for FileField.
            # For clarity, explicitly setting to None if no URL.
            representation['report_file_url'] = None
        return representation
