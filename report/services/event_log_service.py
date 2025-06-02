from report.models.event_log_model import EventLogModel
from typing import Dict, Any, Optional


class EventLogService:
    """Service pour enregistrer les événements système"""

    @staticmethod
    def log_event(event_type: str, message: str, user=None, detection=None,
                  alert=None, region=None, metadata: Dict[str, Any] = None):
        """Enregistre un événement système"""
        try:
            return EventLogModel.objects.create(
                event_type=event_type,
                message=message,
                user=user,
                detection=detection,
                alert=alert,
                region=region,
                metadata=metadata
            )
        except Exception as e:
            print(f"Erreur enregistrement event log: {e}")
            return None

    @staticmethod
    def log_analysis_started(user=None, months_back: int = 3):
        """Log début d'analyse"""
        return EventLogService.log_event(
            'ANALYSIS_STARTED',
            f"Analyse satellite démarrée pour {months_back} mois",
            user=user,
            metadata={'months_back': months_back}
        )

    @staticmethod
    def log_analysis_completed(user=None, results: Dict = None):
        """Log fin d'analyse"""
        message = f"Analyse terminée: {results.get('detections_found', 0)} détections"
        return EventLogService.log_event(
            'ANALYSIS_COMPLETED',
            message,
            user=user,
            metadata=results
        )

    @staticmethod
    def log_detection_created(detection, user=None):
        """Log création détection"""
        message = f"Détection créée: {detection.detection_type} (score: {detection.confidence_score:.2f})"
        return EventLogService.log_event(
            'DETECTION_CREATED',
            message,
            user=user,
            detection=detection,
            region=detection.region
        )

    @staticmethod
    def log_investigation_assigned(investigation, assigned_by=None):
        """Log assignation investigation"""
        message = f"Investigation assignée à {investigation.assigned_to.get_full_name() if investigation.assigned_to else 'N/A'}"
        return EventLogService.log_event(
            'INVESTIGATION_ASSIGNED',
            message,
            user=assigned_by,
            detection=investigation.detection,
            metadata={'investigation_id': investigation.id}
        )
