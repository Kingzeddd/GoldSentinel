# report/services/dashboard_service.py
from typing import Optional, Any, Dict # Added Any, Dict for potential broader use
from datetime import date, timedelta

from django.db.models import Count, Sum, Q, Avg # Ensure Avg is imported if used by other methods later
from django.utils import timezone

from detection.models.detection_model import DetectionModel # Direct import
from alert.models.alert_model import AlertModel # Direct import
from region.models.region_model import RegionModel # Direct import
# from report.models.dashboard_statistic_model import DashboardStatistic # Not used by service directly for calculation


class DashboardService:

    def _apply_filters(self, queryset, region_id: Optional[int] = None, target_date: Optional[date] = None, date_field: str = 'created_at'):
        """Helper to apply common region and date filters."""
        if region_id:
            queryset = queryset.filter(region_id=region_id)

        if target_date:
            # This filter is for matching records exactly on target_date's date part.
            # For date ranges (e.g. "active during date X"), more complex logic might be needed
            # depending on how start/end times of activities are recorded.
            queryset = queryset.filter(**{f'{date_field}__date': target_date})
        return queryset

    def calculate_total_detections(self, region_id: Optional[int] = None, target_date: Optional[date] = None) -> float:
        """Calculates total detections, optionally filtered by region and/or a specific date."""
        qs = DetectionModel.objects.all() # Start with all objects
        # Assuming 'detection_date' is the relevant field in DetectionModel
        qs = self._apply_filters(qs, region_id, target_date, 'detection_date')
        return float(qs.count())

    def calculate_active_alerts(self, region_id: Optional[int] = None, target_date: Optional[date] = None) -> float:
        """
        Calculates active alerts.
        If target_date is provided, it counts alerts that were active and created on that specific date.
        More complex logic would be needed for "active *during* date X but created before".
        """
        # Assuming AlertModel has AlertStatusChoices defined as TextChoices
        qs = AlertModel.objects.filter(alert_status=AlertModel.AlertStatusChoices.ACTIVE)
        qs = self._apply_filters(qs, region_id, target_date, 'created_at') # Filter by creation date
        return float(qs.count())

    def calculate_resolved_alerts(self, region_id: Optional[int] = None, target_date: Optional[date] = None) -> float:
        """
        Calculates resolved alerts.
        If target_date is provided, it counts alerts that were resolved and whose 'updated_at' field falls on that date.
        This uses 'updated_at' as a proxy for resolution time.
        """
        # Assuming AlertModel has AlertStatusChoices defined as TextChoices
        qs = AlertModel.objects.filter(alert_status=AlertModel.AlertStatusChoices.RESOLVED)
        # Using 'updated_at' as a proxy for when the status was changed to RESOLVED.
        # This might not be perfectly accurate if 'updated_at' changes for other reasons.
        # A dedicated 'resolved_at' field would be more precise.
        qs = self._apply_filters(qs, region_id, target_date, 'updated_at')
        return float(qs.count())

    def calculate_validated_detections(self, region_id: Optional[int] = None, target_date: Optional[date] = None) -> float:
        """
        Calculates validated detections (status VALIDATED or CONFIRMED).
        If target_date is provided, it filters by 'validated_at' date.
        """
        # Assuming DetectionModel has ValidationStatusChoices defined as TextChoices
        qs = DetectionModel.objects.filter(
            Q(validation_status=DetectionModel.ValidationStatusChoices.VALIDATED) |
            Q(validation_status=DetectionModel.ValidationStatusChoices.CONFIRMED)
        )
        # Assuming DetectionModel has a 'validated_at' field.
        qs = self._apply_filters(qs, region_id, target_date, 'validated_at')
        return float(qs.count())

    def calculate_deforestation_ha(self, region_id: Optional[int] = None, target_date: Optional[date] = None) -> float:
        """
        Calculates total hectares of deforestation detections.
        If target_date is provided, it filters by 'detection_date'.
        """
        # Assuming DetectionModel has DetectionTypeChoices defined as TextChoices
        qs = DetectionModel.objects.filter(detection_type=DetectionModel.DetectionTypeChoices.DEFORESTATION)
        qs = self._apply_filters(qs, region_id, target_date, 'detection_date')
        total_ha = qs.aggregate(total_area=Sum('area_hectares'))['total_area']
        return float(total_ha or 0.0)

    # Placeholder for other statistic calculations:
    # def calculate_new_mining_sites_monthly(self, region_id: Optional[int] = None, year: int, month: int) -> float:
    #     """Calculates new mining sites detected in a specific month."""
    #     qs = DetectionModel.objects.filter(
    #         detection_type=DetectionModel.DetectionTypeChoices.MINING_SITE,
    #         detection_date__year=year,
    #         detection_date__month=month
    #     )
    #     if region_id:
    #         qs = qs.filter(region_id=region_id)
    #     return float(qs.count())

    # def calculate_water_pollution_incidents(self, region_id: Optional[int] = None, target_date: Optional[date] = None) -> float:
    #     """Calculates water pollution incidents."""
    #     qs = DetectionModel.objects.filter(detection_type=DetectionModel.DetectionTypeChoices.WATER_POLLUTION)
    #     qs = self._apply_filters(qs, region_id, target_date, 'detection_date')
    #     return float(qs.count())

    # Add more methods as defined in DashboardStatistic.StatisticTypeChoices
    # e.g., calculate_total_active_alerts, calculate_total_resolved_alerts etc.
    # The methods above are more specific (daily counts if target_date is used).
    # General total counts (non-daily) would not use the target_date or use it differently.

    # Example for a generic "current value" type of statistic not tied to a specific date of occurrence
    # def get_current_active_alerts_count(self, region_id: Optional[int] = None) -> float:
    #     qs = AlertModel.objects.filter(alert_status=AlertModel.AlertStatusChoices.ACTIVE)
    #     if region_id:
    #         qs = qs.filter(region_id=region_id)
    #     return float(qs.count())
