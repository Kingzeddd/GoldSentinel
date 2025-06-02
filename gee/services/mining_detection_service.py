from typing import List, Dict, Optional
from django.utils import timezone
import tensorflow as tf
import numpy as np
import os
from django.conf import settings

from config.financial_settings import FinancialSettings
from image.models.image_model import ImageModel
from detection.models.detection_model import DetectionModel
from alert.models.alert_model import AlertModel
from alert.models.financial_risk_model import FinancialRiskModel

from gee.services.earth_engine_service import EarthEngineService
from report.services.event_log_service import EventLogService


class MiningDetectionService:
    """Service de détection d'activités d'orpaillage"""

    def __init__(self):
        self.gee_service = EarthEngineService()
        self.model = self._load_tensorflow_model()

    def _load_tensorflow_model(self):
        """Charge le modèle TensorFlow pour la détection"""
        try:
            model_path = os.path.join(settings.BASE_DIR, 'ai', 'models', 'ghana_mining_detector.h5')
            if os.path.exists(model_path):
                model = tf.keras.models.load_model(model_path)
                print(f"Modèle TensorFlow chargé: {model_path}")
                return model
            else:
                print(f"Modèle non trouvé: {model_path}")
                return None
        except Exception as e:
            print(f"Erreur chargement modèle TensorFlow: {e}")
            return None

    def _predict_with_tensorflow(self, latitude: float, longitude: float, image_asset_id: str) -> float:
        """Utilise le modèle TensorFlow pour prédire la probabilité d'orpaillage à partir d'un patch spectral."""
        if not self.model:
            print("Modèle TensorFlow non chargé. Skipping prediction.")
            return 0.0

        try:
            # 1. Obtenir le patch spectral de GEE
            raw_patch_data = self.gee_service.get_spectral_patch(
                point_coords=(longitude, latitude),
                image_asset_id=image_asset_id,
                patch_size_pixels=48, # Doit correspondre à l'attente du modèle
                scale=10 # Résolution Sentinel-2 typique pour ces bandes
            )

            if not raw_patch_data:
                print("Erreur: Impossible de récupérer les données du patch spectral depuis GEE.")
                return 0.0

            if len(raw_patch_data) < 2: # Header + au moins une ligne de données (en fait, on en attend 48*48)
                print(f"Erreur: Données de patch insuffisantes. Reçu {len(raw_patch_data)} lignes.")
                return 0.0

            # 2. Traiter les données brutes en un tableau NumPy (48, 48, 3)
            header = raw_patch_data[0]
            pixel_values_list = raw_patch_data[1:]

            expected_pixels = 48 * 48
            if len(pixel_values_list) != expected_pixels:
                print(f"Erreur: Nombre de pixels incorrect. Attendu {expected_pixels}, reçu {len(pixel_values_list)}.")
                # Tenter de voir si c'est un problème de géométrie/bordure
                # Parfois getRegion peut retourner moins si le patch est au bord de l'image source
                # Pour ce modèle, une taille fixe est cruciale.
                return 0.0

            # Trouver les indices des colonnes NDVI, NDWI, NDTI
            try:
                ndvi_idx = header.index('NDVI')
                ndwi_idx = header.index('NDWI')
                ndti_idx = header.index('NDTI')
            except ValueError as e:
                print(f"Erreur: Une ou plusieurs colonnes d'indice manquantes dans l'en-tête GEE: {header}. Détail: {e}")
                return 0.0

            # Extraire et remodeler chaque bande
            # GEE peut retourner None pour les pixels masqués ou en dehors de la couverture image.
            # Il faut gérer ces None, par exemple en les remplaçant par 0 ou une valeur spécifique.
            # Le defaultValue=0 dans getRegion devrait gérer ça, mais vérifions.
            def extract_band(idx):
                band_flat = []
                for p in pixel_values_list:
                    val = p[idx]
                    band_flat.append(float(val) if val is not None else 0.0) # Gérer les None potentiels
                return np.array(band_flat, dtype=np.float32).reshape((48, 48))

            ndvi_array = extract_band(ndvi_idx)
            ndwi_array = extract_band(ndwi_idx)
            ndti_array = extract_band(ndti_idx)

            # Empiler les bandes pour former l'image (48, 48, 3)
            spectral_patch_np = np.stack([ndvi_array, ndwi_array, ndti_array], axis=-1)

            if spectral_patch_np.shape != (48, 48, 3):
                print(f"Erreur: La forme du patch spectral final est incorrecte: {spectral_patch_np.shape}")
                return 0.0

            # 3. Préparer l'entrée du modèle et prédire
            model_input = np.expand_dims(spectral_patch_np, axis=0)  # Ajoute la dimension du batch -> (1, 48, 48, 3)

            prediction = self.model.predict(model_input, verbose=0)
            confidence = float(prediction[0][0]) # Supposant que le modèle sort une seule valeur par item de batch

            return min(max(confidence, 0.0), 1.0)  # Clamp entre 0 et 1

        except Exception as e:
            print(f"Erreur lors de la prédiction TensorFlow avec patch spectral: {e}")
            return 0.0

    def analyze_for_mining_activity(self, image_record: 'ImageModel') -> List[DetectionModel]:
        """
        Analyse une image pour détecter activités d'orpaillage

        Args:
            image_record: Enregistrement image à analyser

        Returns:
            Liste des détections trouvées
        """
        detections = []

        try:
            # Récupération image de référence (plus ancienne disponible)
            reference_image = (ImageModel.objects
                               .filter(region=image_record.region,
                                       processing_status='COMPLETED')
                               .exclude(id=image_record.id)
                               .order_by('capture_date')
                               .first())

            if not reference_image:
                print("Pas d'image de référence trouvée")
                return detections

            # Comparaison indices spectraux
            current_indices = {
                'ndvi_data': image_record.ndvi_data,
                'ndwi_data': image_record.ndwi_data,
                'ndti_data': image_record.ndti_data,
            }

            reference_indices = {
                'ndvi_data': reference_image.ndvi_data,
                'ndwi_data': reference_image.ndwi_data,
                'ndti_data': reference_image.ndti_data,
            }

            # Détection anomalies
            anomaly_scores = self.gee_service.detect_anomalies(current_indices, reference_indices)

            # Prédiction TensorFlow en utilisant le centre de l'image pour le patch
            # Idéalement, on itérerait sur des points d'intérêt ou des grilles.
            # Pour l'instant, on utilise le centre de l'image comme point pour le patch.
            tf_confidence = 0.0
            if image_record.center_lat is not None and image_record.center_lon is not None and image_record.gee_asset_id:
                tf_confidence = self._predict_with_tensorflow(
                    latitude=image_record.center_lat,
                    longitude=image_record.center_lon,
                    image_asset_id=image_record.gee_asset_id
                )
            else:
                print(f"Avertissement: Coordonnées du centre ou GEE asset ID manquants pour l'image {image_record.id}. Skipping TF prediction.")


            # Seuils de détection (à calibrer selon vos données)
            DETECTION_THRESHOLDS = {
                'ndvi_threshold': 0.3,  # Chute significative végétation
                'ndwi_threshold': 0.2,  # Changement eau/turbidité
                'ndti_threshold': 0.4,  # Perturbation sol
                'tf_threshold': 0.5,    # Seuil modèle TensorFlow
            }

            # Vérification seuils dépassés (anomalies OU modèle TensorFlow)
            anomaly_detected = (anomaly_scores.get('ndvi_anomaly_score', 0) > DETECTION_THRESHOLDS['ndvi_threshold'] or
                               anomaly_scores.get('ndwi_anomaly_score', 0) > DETECTION_THRESHOLDS['ndwi_threshold'] or
                               anomaly_scores.get('ndti_anomaly_score', 0) > DETECTION_THRESHOLDS['ndti_threshold'])

            tf_detected = tf_confidence > DETECTION_THRESHOLDS['tf_threshold']

            if anomaly_detected or tf_detected:
                # Création détection
                detection = DetectionModel.objects.create(
                    image=image_record,
                    region=image_record.region,
                    latitude=image_record.center_lat,
                    longitude=image_record.center_lon,
                    detection_type='MINING_SITE',  # Type principal
                    confidence_score=0,  # Calculé ci-dessous
                    area_hectares=self._estimate_affected_area(anomaly_scores),
                    ndvi_anomaly_score=anomaly_scores.get('ndvi_anomaly_score'),
                    ndwi_anomaly_score=anomaly_scores.get('ndwi_anomaly_score'),
                    ndti_anomaly_score=anomaly_scores.get('ndti_anomaly_score'),
                    validation_status='DETECTED'
                )

                # Calcul score confiance combiné (anomalies + TensorFlow)
                anomaly_confidence = detection.calculate_confidence_score()
                combined_confidence = (anomaly_confidence * 0.6) + (tf_confidence * 0.4)
                detection.confidence_score = min(max(combined_confidence, 0.0), 1.0)
                detection.save()

                detections.append(detection)

                # Génération alerte et risque financier
                self._generate_alert_and_risk(detection)

                # LOG ÉVÉNEMENT
                EventLogService.log_detection_created(detection)

                detections.append(detection)
                self._generate_alert_and_risk(detection)

            return detections

        except Exception as e:
            EventLogService.log_event(
                'SYSTEM_ERROR',
                f"Erreur analyse activité minière: {str(e)}",
                metadata={'image_id': image_record.id}
            )
            return detections

    def _estimate_affected_area(self, anomaly_scores: Dict) -> float:
        """Estime la surface affectée basée sur les scores d'anomalie"""
        # Logique simplifiée - à améliorer avec données réelles
        max_score = max(anomaly_scores.values())
        # Surface proportionnelle au score (1-50 hectares)
        return min(max_score * 50, 50)

    # Dans detection/services/mining_detection_service.py
    def _generate_alert_and_risk(self, detection: DetectionModel):
        """Génère alerte, risque financier ET investigation automatiquement"""
        try:
            # 1. Détermination type d'alerte selon score
            if detection.confidence_score >= 0.8:
                alert_type = 'CLANDESTINE_SITE'
                criticality = 'CRITICAL'
            elif detection.confidence_score >= 0.6:
                alert_type = 'SUSPICIOUS_ACTIVITY'
                criticality = 'HIGH'
            else:
                alert_type = 'SUSPICIOUS_ACTIVITY'
                criticality = 'MEDIUM'

            # 2. Création alerte
            alert = AlertModel.objects.create(
                name=f"Détection orpaillage - {detection.detection_date.strftime('%Y-%m-%d')}",
                detection=detection,
                region=detection.region,
                level=criticality,
                alert_type=alert_type,
                message=f"Activité d'orpaillage détectée avec un score de confiance de {detection.confidence_score:.2f}. "
                        f"Surface estimée: {detection.area_hectares:.1f} hectares.",
                alert_status='ACTIVE'
            )

            # LOG ALERTE
            EventLogService.log_event(
                'ALERT_GENERATED',
                f"Alerte {criticality} générée pour détection {detection.id}",
                detection=detection,
                alert=alert
            )

            # 3. Création risque financier
            financial_risk = FinancialRiskModel.objects.create(
                detection=detection,
                area_hectares=detection.area_hectares,
                cost_per_hectare=FinancialSettings.DEFAULT_COST_PER_HECTARE,
                sensitive_zone_distance_km=2.0,
                occurrence_count=1
            )

            # LOG RISQUE
            EventLogService.log_event(
                'FINANCIAL_RISK_CALCULATED',
                f"Risque financier calculé: {financial_risk.estimated_loss:,.0f} FCFA",
                detection=detection,
                metadata={'risk_level': financial_risk.risk_level, 'amount': financial_risk.estimated_loss}
            )

            # Calculs automatiques
            financial_risk.calculate_estimated_loss()
            financial_risk.risk_level = financial_risk.determine_risk_level()
            financial_risk.save()

            # 4. NOUVEAU : Création automatique investigation
            from detection.models.investigation_model import InvestigationModel

            investigation = InvestigationModel.objects.create(
                detection=detection,
                target_coordinates=f"{detection.latitude:.4f}, {detection.longitude:.4f}",
                access_instructions=f"Zone Bondoukou - Coordonnées GPS: {detection.latitude:.4f}, {detection.longitude:.4f}. "
                                    f"Surface estimée: {detection.area_hectares:.1f} hectares. "
                                    f"Confidence IA: {detection.confidence_score:.2f}",
                status='PENDING'
            )

            print(f"Alerte, risque financier et investigation créés pour détection {detection.id}")
            # LOG INVESTIGATION
            EventLogService.log_event(
                'INVESTIGATION_CREATED',
                f"Investigation créée automatiquement pour détection {detection.id}",
                detection=detection,
                metadata={'investigation_id': investigation.id}
            )

        except Exception as e:
            EventLogService.log_event(
                'SYSTEM_ERROR',
                f"Erreur génération alerte/risque/investigation: {str(e)}",
                detection=detection
            )