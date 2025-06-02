# report/services/report_service.py
import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Callable # Callable might not be used yet, but good for typing

from django.db.models import Count, Q, Avg, Min, Max # Q, Avg, Min, Max added for potential use

from detection.models import DetectionModel, InvestigationModel
from alert.models import AlertModel
from region.models import RegionModel
from image.models import ImageModel # Added ImageModel

class ReportService:

    def _generate_csv_content(self, headers: List[str], data_rows: List[List[Any]]) -> str:
        """Helper function to generate CSV content as a string."""
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(headers)
        writer.writerows(data_rows)
        return csv_buffer.getvalue()

    def generate_summary_report(self, start_date_str: str = None, end_date_str: str = None) -> Dict[str, Any]:
        """Generates a system-wide summary report."""
        # Query data
        detections_count = DetectionModel.objects.count()
        alerts_count = AlertModel.objects.count()
        investigations_count = InvestigationModel.objects.count()

        regions_count = RegionModel.objects.count()
        images_processed_count = ImageModel.objects.filter(processing_status=ImageModel.ProcessingStatus.COMPLETED).count()

        # Basic stats for detections
        avg_confidence_result = DetectionModel.objects.aggregate(avg_conf=Avg('confidence_score'))
        avg_confidence = avg_confidence_result['avg_conf'] if avg_confidence_result['avg_conf'] is not None else 0.0

        headers = ['Metric', 'Value']
        data_rows = [
            ['Total Detections', detections_count],
            ['Total Alerts', alerts_count],
            ['Total Investigations', investigations_count],
            ['Total Regions Monitored', regions_count],
            ['Total Images Processed', images_processed_count],
            ['Average Detection Confidence', f"{avg_confidence:.2f}"],
        ]

        # Date filtering (example, can be more sophisticated)
        # if start_date_str and end_date_str:
        #     # Convert str dates to datetime objects
        #     start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
        #     end_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
        #     # Apply date filters to queries above, e.g.:
        #     # detections_count = DetectionModel.objects.filter(created_at__range=(start_dt, end_dt)).count()
        #     # ... and so on for other metrics ...
        #     pass

        csv_content = self._generate_csv_content(headers, data_rows)
        filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return {"filename": filename, "content": csv_content, "content_type": "text/csv"}

    def generate_alert_summary_report(self, region_id: int = None, start_date_str: str = None, end_date_str: str = None) -> Dict[str, Any]:
        """Generates a summary of alerts, optionally filtered by region and date."""
        alerts_query = AlertModel.objects.all()
        report_title_suffix = "all_regions"
        region_name_for_file = "all"

        if region_id:
            try:
                # Ensure region_id is an integer if it's passed as a string from some sources
                valid_region_id = int(region_id)
                alerts_query = alerts_query.filter(region_id=valid_region_id)
                region = RegionModel.objects.get(id=valid_region_id)
                report_title_suffix = f"region_{region.name.lower().replace(' ', '_')}"
                region_name_for_file = region.name.lower().replace(' ', '_')
            except RegionModel.DoesNotExist:
                # If region_id is provided but not found, perhaps return empty or error, or report for all
                # For now, let's assume an invalid region_id means no specific region filter applied or handle as error.
                # This implementation will just result in an empty filter if region_id is invalid and not found.
                # To be safe, let's default to all if region not found, or raise error.
                # For this example, we'll just use the id in the suffix if name not found.
                report_title_suffix = f"region_id_{region_id}"
                region_name_for_file = f"id_{region_id}"
            except ValueError: # Handle case where region_id is not a valid integer
                self.stdout.write(self.style.WARNING(f"Invalid region_id format: {region_id}. Reporting for all regions."))
                # Fallback to all regions if region_id is invalid format
                pass

        # Date filtering example (add to queries as needed)
        # if start_date_str and end_date_str:
        #     try:
        #         start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
        #         end_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
        #         alerts_query = alerts_query.filter(created_at__range=(start_dt, end_dt))
        #         report_title_suffix += f"_from_{start_date_str}_to_{end_date_str}"
        #     except ValueError:
        #          # Handle incorrect date format if necessary
        #         pass


        headers = ['ID', 'Detection ID', 'Region', 'Type', 'Level', 'Status', 'Created At', 'Message']
        data_rows = []
        for alert in alerts_query.select_related('detection', 'region').order_by('-created_at'):
            data_rows.append([
                alert.id,
                alert.detection_id if alert.detection else 'N/A', # Handle if detection is None
                alert.region.name if alert.region else 'N/A',
                alert.get_alert_type_display(),
                alert.get_level_display(),
                alert.get_alert_status_display(),
                alert.created_at.strftime('%Y-%m-%d %H:%M') if alert.created_at else 'N/A',
                alert.message
            ])

        csv_content = self._generate_csv_content(headers, data_rows)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"alert_summary_{region_name_for_file}_{timestamp}.csv"

        return {"filename": filename, "content": csv_content, "content_type": "text/csv"}

    # Add other report generation methods here based on ReportModel.REPORT_TYPES:
    # - def generate_region_detail_report(self, region_id: int, start_date_str: str = None, end_date_str: str = None) -> Dict[str, Any]:
    #     # Detailed statistics for a specific region: active detections, investigations by status, etc.
    #     pass

    # - def generate_deforestation_trend_report(self, region_id: int = None, period_months: int = 12) -> Dict[str, Any]:
    #     # Monthly deforestation stats (e.g., area_hectares from 'DEFORESTATION' type detections)
    #     pass

    # - def generate_water_quality_trend_report(self, region_id: int = None, period_months: int = 12) -> Dict[str, Any]:
    #     # Monthly water quality stats (e.g., from 'WATER_POLLUTION' type detections or specific metrics)
    #     pass

    # These would involve more complex queries and data aggregation.
    # For now, the two examples (summary_report, alert_summary_report) are sufficient for the subtask.
