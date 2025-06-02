# config/detection_settings.py

class DetectionConfig:
    """
    Configuration settings for the mining detection process,
    thresholds for alerts, and confidence score calculations.
    """

    # Thresholds for triggering a detection based on individual spectral anomaly scores
    # These values are compared against the calculated anomaly_scores from EarthEngineService.detect_anomalies
    SPECTRAL_NDVI_THRESHOLD: float = 0.3  # Minimum NDVI anomaly score to be considered significant
    SPECTRAL_NDWI_THRESHOLD: float = 0.2  # Minimum NDWI anomaly score to be considered significant
    SPECTRAL_NDTI_THRESHOLD: float = 0.4  # Minimum NDTI anomaly score to be considered significant

    # Threshold for the TensorFlow model's output score
    TENSORFLOW_SCORE_THRESHOLD: float = 0.5 # Minimum confidence from TF model to be considered significant

    # Weights for calculating the initial 'anomaly_confidence' in DetectionModel.calculate_confidence_score
    # This score is derived purely from spectral anomalies.
    # The sum of these weights should ideally be 1.0 if it's a direct weighted average.
    ANOMALY_CONFIDENCE_WEIGHT_NDVI: float = 0.4
    ANOMALY_CONFIDENCE_WEIGHT_NDWI: float = 0.3
    ANOMALY_CONFIDENCE_WEIGHT_NDTI: float = 0.3

    # Weights for combining the 'anomaly_confidence' (from spectral indices)
    # and 'tf_confidence' (from TensorFlow model) into the final detection.confidence_score.
    # The sum of these weights should ideally be 1.0.
    COMBINED_CONFIDENCE_WEIGHT_ANOMALY: float = 0.6 # Weight for the anomaly_confidence part
    COMBINED_CONFIDENCE_WEIGHT_TF: float = 0.4      # Weight for the TensorFlow prediction part

    # Thresholds for determining alert criticality based on the final detection.confidence_score
    # As used in MiningDetectionService._generate_alert_and_risk
    ALERT_CRITICALITY_THRESHOLD_CRITICAL: float = 0.8 # Score >= this is CRITICAL
    ALERT_CRITICALITY_THRESHOLD_HIGH: float = 0.6    # Score >= this (and < CRITICAL_THRESHOLD) is HIGH
                                                     # Score < HIGH_THRESHOLD is MEDIUM (implicitly)

    # Example of how to potentially make the area estimation configurable too
    # (Currently, _estimate_affected_area in MiningDetectionService uses a simple logic)
    # MAX_AFFECTED_AREA_ESTIMATE_HECTARES: float = 50.0
    # SCORE_TO_HECTARES_MULTIPLIER: float = 50.0

    # Placeholder for any other detection-related settings
    # For example, parameters for patch extraction if they need to be centralized
    # DEFAULT_PATCH_SIZE_PIXELS: int = 48
    # DEFAULT_GEE_SCALE_METERS: int = 10
