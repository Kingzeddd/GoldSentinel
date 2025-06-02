from base.models.helpers.date_time_model import DateTimeModel
from django.db import models

class DetectionFeedbackModel(DateTimeModel):
    """Stockage feedback terrain pour améliorer IA"""

    detection = models.OneToOneField('detection.DetectionModel', on_delete=models.CASCADE)
    investigation = models.OneToOneField('detection.InvestigationModel', on_delete=models.CASCADE)

    # Scores IA au moment détection
    original_confidence = models.FloatField()
    original_ndvi_score = models.FloatField()
    original_ndwi_score = models.FloatField()
    original_ndti_score = models.FloatField()

    # Vérité terrain
    ground_truth_confirmed = models.BooleanField()  # Agent confirme ?
    agent_confidence = models.IntegerField(choices=[(1, 'Faible'), (2, 'Moyen'), (3, 'Élevé')])

    # Utilisation future : ajustement seuils
    used_for_training = models.BooleanField(default=False)

    class Meta:
        db_table = 'detection_feedbacks'
        verbose_name = 'Detection Feedback'
        verbose_name_plural = 'Detection Feedbacks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ground_truth_confirmed', 'used_for_training']),
        ]

    def __str__(self):
        status = "Confirmé" if self.ground_truth_confirmed else "Infirmé"
        return f"Feedback {self.detection.id} - {status}"