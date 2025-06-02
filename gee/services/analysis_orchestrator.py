# analysis/services/analysis_orchestrator.py
from datetime import datetime, timedelta
from typing import List, Dict

from gee.services.earth_engine_service import EarthEngineService
from gee.services.mining_detection_service import MiningDetectionService

from report.services.event_log_service import EventLogService


class AnalysisOrchestrator:
    """Service orchestrateur pour analyses complètes"""

    def __init__(self):
        self.gee_service = EarthEngineService()
        self.detection_service = MiningDetectionService()

    def run_complete_analysis(self, months_back: int = 3, user_id: int = None) -> Dict:
        """
        Lance une analyse complète de détection d'orpaillage

        Args:
            months_back: Période d'analyse en mois
            user_id: ID utilisateur demandant l'analyse

        Returns:
            Résultats de l'analyse complète
        """
        results = {
            'success': False,
            'images_processed': 0,
            'detections_found': 0,
            'alerts_generated': 0,
            'errors': []
        }

        try:
            # Récupération utilisateur pour logging
            user = None
            if user_id:
                from account.models.user_model import UserModel
                user = UserModel.objects.filter(id=user_id).first()

            # LOG DÉBUT ANALYSE
            EventLogService.log_analysis_started(user, months_back)
            print(f"DEBUG: Début analyse pour {months_back} mois")

            # 1. Récupération images récentes
            print("Récupération images satellites récentes...")
            recent_images = self.gee_service.get_recent_images(months_back)
            print(f"DEBUG: Récupéré {len(recent_images)} images")

            if not recent_images:
                error_msg = "Aucune image satellite trouvée"
                print(f"DEBUG: {error_msg}")
                results['errors'].append(error_msg)

                # Log erreur
                EventLogService.log_event(
                    'SYSTEM_ERROR',
                    error_msg,
                    user=user,
                    metadata={'months_back': months_back}
                )

                # Marquer comme succès même sans images (pas une erreur système)
                results['success'] = True
                return results

            print(f"Trouvé {len(recent_images)} images disponibles")

            # 2. Traitement de chaque image
            total_detections = []

            for img_data in recent_images[-5:]:  # Limite 5 images les plus récentes pour MVP
                print(f"Traitement image {img_data['gee_asset_id']}...")

                try:
                    # Traitement image complète
                    image_record = self.gee_service.process_image_complete(
                        img_data['gee_asset_id'],
                        user_id
                    )

                    if image_record and image_record.processing_status == 'COMPLETED':
                        results['images_processed'] += 1

                        # Log traitement image réussi
                        EventLogService.log_event(
                            'IMAGE_PROCESSED',
                            f"Image {image_record.name} traitée avec succès",
                            user=user,
                            metadata={
                                'image_id': image_record.id,
                                'gee_asset_id': img_data['gee_asset_id'],
                                'capture_date': image_record.capture_date.isoformat()
                            }
                        )

                        # Analyse détection orpaillage
                        detections = self.detection_service.analyze_for_mining_activity(image_record)
                        total_detections.extend(detections)

                        print(f"  → {len(detections)} détections trouvées")

                    else:
                        error_msg = f"Erreur traitement {img_data['gee_asset_id']}"
                        results['errors'].append(error_msg)
                        print(f"  → {error_msg}")

                        # Log erreur traitement image
                        EventLogService.log_event(
                            'SYSTEM_ERROR',
                            error_msg,
                            user=user,
                            metadata={
                                'gee_asset_id': img_data['gee_asset_id'],
                                'error_type': 'image_processing_failed'
                            }
                        )

                except Exception as e:
                    error_msg = f"Erreur traitement image {img_data['gee_asset_id']}: {str(e)}"
                    results['errors'].append(error_msg)
                    print(f"  → {error_msg}")

                    # Log erreur exception
                    EventLogService.log_event(
                        'SYSTEM_ERROR',
                        error_msg,
                        user=user,
                        metadata={
                            'gee_asset_id': img_data['gee_asset_id'],
                            'error_type': 'processing_exception',
                            'exception': str(e)
                        }
                    )

            # 3. Calcul résultats finaux
            results['success'] = True
            results['detections_found'] = len(total_detections)
            results['alerts_generated'] = sum(1 for d in total_detections if hasattr(d, 'alerts') and d.alerts.exists())

            print(f"Analyse terminée: {results['detections_found']} détections trouvées")

            # LOG FIN ANALYSE AVEC RÉSULTATS
            EventLogService.log_analysis_completed(user, {
                'images_processed': results['images_processed'],
                'detections_found': results['detections_found'],
                'alerts_generated': results['alerts_generated'],
                'errors_count': len(results['errors']),
                'success': results['success']
            })

            # Log détaillé des résultats
            if results['detections_found'] > 0:
                EventLogService.log_event(
                    'ANALYSIS_COMPLETED',
                    f"Analyse terminée avec succès: {results['detections_found']} détections, "
                    f"{results['alerts_generated']} alertes générées sur {results['images_processed']} images",
                    user=user,
                    metadata=results
                )

        except Exception as e:
            error_msg = f"Erreur analyse complète: {str(e)}"
            results['errors'].append(error_msg)
            results['success'] = False
            print(f"Erreur dans l'orchestrateur: {e}")

            # LOG ERREUR CRITIQUE
            EventLogService.log_event(
                'SYSTEM_ERROR',
                error_msg,
                user=user,
                metadata={
                    'months_back': months_back,
                    'error_type': 'analysis_orchestrator_failure',
                    'exception': str(e)
                }
            )

        return results