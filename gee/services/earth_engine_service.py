import ee
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from django.utils import timezone

from gee.config import GEEConfig
from image.models.image_model import ImageModel
from region.models.region_model import RegionModel
from ..tasks import process_gee_image_task # Import the new Celery task


class EarthEngineService:
    """Service principal pour interactions avec Google Earth Engine"""

    def __init__(self):
        self.initialized = GEEConfig.initialize_ee()
        if not self.initialized:
            raise Exception("Impossible d'initialiser Google Earth Engine")

    def get_recent_images(self, months_back: int = 3) -> List[Dict]:
        """
        Récupère les images satellites récentes pour Bondoukou

        Args:
            months_back: Nombre de mois en arrière (défaut: 3)

        Returns:
            Liste des images disponibles avec métadonnées
        """
        try:
            # Calcul période
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months_back * 30)

            # Zone Bondoukou
            bondoukou_geom = GEEConfig.get_bondoukou_geometry()

            # Collection Sentinel-2
            # Ajout debug
            print(f"Recherche images du {start_date} au {end_date}")
            print(f"Zone: {bondoukou_geom.getInfo()}")

            collection = (ee.ImageCollection(GEEConfig.SENTINEL2_COLLECTION)
                          .filterBounds(bondoukou_geom)
                          .filterDate(start_date.strftime('%Y-%m-%d'),
                                      end_date.strftime('%Y-%m-%d'))
                          .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',
                                               GEEConfig.MAX_CLOUD_COVERAGE)))

            print(f"Images trouvées: {collection.size().getInfo()}")

            # Récupération métadonnées
            image_list = collection.getInfo()

            images_data = []
            for img_info in image_list.get('features', []):
                properties = img_info['properties']

                images_data.append({
                    'gee_asset_id': img_info['id'],
                    'capture_date': datetime.fromtimestamp(
                        properties['system:time_start'] / 1000
                    ).date(),
                    'cloud_coverage': properties.get('CLOUDY_PIXEL_PERCENTAGE', 0),
                    'satellite_source': 'SENTINEL2',
                    'resolution': 10,  # Sentinel-2 10m
                    'properties': properties
                })

            return images_data

        except Exception as e:
            print(f"Erreur récupération images: {e}")
            return []

    def calculate_spectral_indices(self, gee_asset_id: str) -> Dict:
        """
        Calcule les indices spectraux NDVI, NDWI, NDTI pour une image

        Args:
            gee_asset_id: ID de l'asset Google Earth Engine

        Returns:
            Dictionnaire avec les données des indices
        """
        try:
            # Chargement image
            image = ee.Image(gee_asset_id)
            bondoukou_geom = GEEConfig.get_bondoukou_geometry()

            # Clip sur zone Bondoukou
            image_clipped = image.clip(bondoukou_geom)

            # Calcul NDVI = (NIR - Red) / (NIR + Red)
            ndvi = image_clipped.normalizedDifference(['B8', 'B4']).rename('NDVI')

            # Calcul NDWI = (Green - NIR) / (Green + NIR)
            ndwi = image_clipped.normalizedDifference(['B3', 'B8']).rename('NDWI')

            # Calcul NDTI = (SWIR1 - SWIR2) / (SWIR1 + SWIR2)
            ndti = image_clipped.normalizedDifference(['B11', 'B12']).rename('NDTI')

            # Statistiques des indices sur la zone
            ndvi_stats = ndvi.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    ee.Reducer.stdDev(), sharedInputs=True
                ),
                geometry=bondoukou_geom,
                scale=10,
                maxPixels=1e9
            ).getInfo()

            ndwi_stats = ndwi.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    ee.Reducer.stdDev(), sharedInputs=True
                ),
                geometry=bondoukou_geom,
                scale=10,
                maxPixels=1e9
            ).getInfo()

            ndti_stats = ndti.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    ee.Reducer.stdDev(), sharedInputs=True
                ),
                geometry=bondoukou_geom,
                scale=10,
                maxPixels=1e9
            ).getInfo()

            return {
                'ndvi_data': {
                    'mean': ndvi_stats.get('NDVI_mean'),
                    'stddev': ndvi_stats.get('NDVI_stdDev'),
                    'computed_at': timezone.now().isoformat()
                },
                'ndwi_data': {
                    'mean': ndwi_stats.get('NDWI_mean'),
                    'stddev': ndwi_stats.get('NDWI_stdDev'),
                    'computed_at': timezone.now().isoformat()
                },
                'ndti_data': {
                    'mean': ndti_stats.get('NDTI_mean'),
                    'stddev': ndti_stats.get('NDTI_stdDev'),
                    'computed_at': timezone.now().isoformat()
                }
            }

        except Exception as e:
            print(f"Erreur calcul indices spectraux: {e}")
            return {}

    def detect_anomalies(self, current_indices: Dict, reference_indices: Dict) -> Dict:
        """
        Détecte les anomalies en comparant indices actuels vs référence

        Args:
            current_indices: Indices de l'image actuelle
            reference_indices: Indices de référence (baseline)

        Returns:
            Scores d'anomalie pour chaque indice
        """
        try:
            anomaly_scores = {}

            for index_name in ['ndvi', 'ndwi', 'ndti']:
                current_data = current_indices.get(f'{index_name}_data', {})
                reference_data = reference_indices.get(f'{index_name}_data', {})

                current_mean = current_data.get('mean')
                reference_mean = reference_data.get('mean')
                reference_stddev = reference_data.get('stddev', 0.1)  # Éviter division par 0

                if current_mean is not None and reference_mean is not None:
                    # Score d'anomalie = différence normalisée
                    anomaly_score = abs(current_mean - reference_mean) / reference_stddev
                    # Normalisation 0-1
                    anomaly_scores[f'{index_name}_anomaly_score'] = min(anomaly_score, 1.0)
                else:
                    anomaly_scores[f'{index_name}_anomaly_score'] = 0.0

            return anomaly_scores

        except Exception as e:
            print(f"Erreur détection anomalies: {e}")
            return {}

    def generate_spectral_maps(self, gee_asset_id: str) -> Dict:
        """
        Génère les cartes de visualisation des indices spectraux

        Args:
            gee_asset_id: ID de l'asset Google Earth Engine

        Returns:
            URLs des cartes de visualisation
        """
        try:
            # Chargement image
            image = ee.Image(gee_asset_id)
            bondoukou_geom = GEEConfig.get_bondoukou_geometry()

            # Clip sur zone Bondoukou
            image_clipped = image.clip(bondoukou_geom)

            # Calcul indices
            ndvi = image_clipped.normalizedDifference(['B8', 'B4']).rename('NDVI')
            ndwi = image_clipped.normalizedDifference(['B3', 'B8']).rename('NDWI')
            ndti = image_clipped.normalizedDifference(['B11', 'B12']).rename('NDTI')

            # Paramètres de visualisation
            ndvi_vis = {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}
            ndwi_vis = {'min': -1, 'max': 1, 'palette': ['white', 'blue']}
            ndti_vis = {'min': -1, 'max': 1, 'palette': ['blue', 'white', 'red']}

            # Génération URLs de tuiles
            ndvi_url = ndvi.getMapId(ndvi_vis)['tile_fetcher'].url_format
            ndwi_url = ndwi.getMapId(ndwi_vis)['tile_fetcher'].url_format
            ndti_url = ndti.getMapId(ndti_vis)['tile_fetcher'].url_format

            return {
                'ndvi_map_url': ndvi_url,
                'ndwi_map_url': ndwi_url,
                'ndti_map_url': ndti_url,
                'bounds': {
                    'north': GEEConfig.BONDOUKOU_BOUNDS['lat_max'],
                    'south': GEEConfig.BONDOUKOU_BOUNDS['lat_min'],
                    'east': GEEConfig.BONDOUKOU_BOUNDS['lon_max'],
                    'west': GEEConfig.BONDOUKOU_BOUNDS['lon_min']
                }
            }

        except Exception as e:
            print(f"Erreur génération cartes spectrales: {e}")
            return {}

    def get_spectral_patch(self, point_coords: Tuple[float, float],
                           patch_size_pixels: int = 48,
                           scale: int = 10,
                           image_asset_id: str) -> Optional[List]:
        """
        Extrait un patch de données spectrales (NDVI, NDWI, NDTI) pour un point donné.

        Args:
            point_coords: Tuple (longitude, latitude) du centre du patch.
            patch_size_pixels: Taille du patch en pixels (défaut: 48).
            scale: Résolution en mètres par pixel (défaut: 10).
            image_asset_id: ID de l'asset Google Earth Engine.

        Returns:
            Liste de listes contenant les données brutes du patch (incluant header),
            ou None si une erreur survient.
        """
        if not self.initialized:
            print("Erreur: GEE n'est pas initialisé.")
            return None

        try:
            image = ee.Image(image_asset_id)

            # Définir le point central
            point = ee.Geometry.Point(point_coords)

            # Calculer la taille du buffer en mètres pour obtenir un carré
            # La moitié de la taille totale du patch en mètres
            buffer_radius_meters = (patch_size_pixels * scale) / 2

            # Créer une géométrie carrée (patch)
            # buffer().bounds() est une bonne approximation pour un carré autour d'un point.
            patch_geometry = point.buffer(buffer_radius_meters).bounds(proj='EPSG:4326', maxError=1)

            # Calculer les indices spectraux (sans clip initial à une grande région)
            # Les bandes sont nommées Bx pour Sentinel-2. S'adapter si autre source.
            ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
            ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI') # Standard NDWI: (Green - NIR) / (Green + NIR)
            ndti = image.normalizedDifference(['B11', 'B12']).rename('NDTI') # Tirsoreh's NDTI: (SWIR1 - SWIR2) / (SWIR1 + SWIR2)

            # Empiler les indices en une seule image à 3 bandes
            stacked_indices = ee.Image.cat([ndvi, ndwi, ndti])

            # Extraire les données pour la région du patch
            # getRegion retourne une liste de listes, la première ligne est l'en-tête.
            patch_data = stacked_indices.getRegion(
                geometry=patch_geometry,
                scale=scale
            ).getInfo() # getInfo() exécute le calcul et récupère les données côté client

            return patch_data

        except ee.EEException as e:
            print(f"Erreur GEE lors de l'extraction du patch: {e}")
            return None
        except Exception as e:
            print(f"Erreur générale lors de l'extraction du patch: {e}")
            return None

    def process_image_complete(self, gee_asset_id: str, user_id: int = None) -> Optional[ImageModel]:
        """
        Traitement complet d'une image : calcul indices + sauvegarde DB

        Args:
            gee_asset_id: ID asset Google Earth Engine
            user_id: ID utilisateur ayant demandé l'analyse

        Returns:
            Instance ImageModel créée (avec statut PENDING) ou existante, ou None si erreur de création initiale.
        """
        try:
            # VÉRIFICATION SI IMAGE EXISTE DÉJÀ ET EST COMPLÉTÉE
            existing_image = ImageModel.objects.filter(
                gee_asset_id=gee_asset_id,
                processing_status=ImageModel.ProcessingStatus.COMPLETED
            ).first()

            if existing_image:
                print(f"Image {gee_asset_id} déjà COMPLETED, récupération...")
                return existing_image

            # Vérifier si une image PENDING ou PROCESSING existe déjà pour éviter les doublons de tâches
            # On pourrait ajouter une logique pour vérifier l'âge de ces tâches ici.
            pending_or_processing_image = ImageModel.objects.filter(
                gee_asset_id=gee_asset_id,
                processing_status__in=[ImageModel.ProcessingStatus.PENDING, ImageModel.ProcessingStatus.PROCESSING]
            ).first()

            if pending_or_processing_image:
                print(f"Image {gee_asset_id} est déjà en cours de traitement ou en attente. ID: {pending_or_processing_image.id}")
                # Optionnel: relancer la tâche si elle semble bloquée (ex: trop vieille)
                # For now, just return the existing record.
                return pending_or_processing_image


            # Récupération métadonnées image depuis GEE
            image_ee = ee.Image(gee_asset_id)
            properties = image_ee.getInfo()['properties'] # Peut lever une ee.EEException

            # Récupération région Bondoukou (ou création si n'existe pas)
            bondoukou_region, _ = RegionModel.objects.get_or_create(
                name='BONDOUKOU',
                defaults={
                    'code': 'BDK', 'area_km2': 12000, # Valeurs par défaut
                    'center_lat': GEEConfig.BONDOUKOU_CENTER[1],
                    'center_lon': GEEConfig.BONDOUKOU_CENTER[0]
                }
            )

            # Création de l'enregistrement ImageModel avec statut PENDING
            image_record = ImageModel.objects.create(
                name=f"Sentinel2_{datetime.fromtimestamp(properties['system:time_start'] / 1000).strftime('%Y%m%d_%H%M%S')}",
                region=bondoukou_region,
                capture_date=datetime.fromtimestamp(properties['system:time_start'] / 1000).date(),
                satellite_source='SENTINEL2', # Assumant Sentinel-2
                cloud_coverage=properties.get('CLOUDY_PIXEL_PERCENTAGE', 0),
                resolution=10, # Résolution typique Sentinel-2 pour les bandes utilisées
                gee_asset_id=gee_asset_id,
                gee_collection=GEEConfig.SENTINEL2_COLLECTION, # Stocker la collection peut être utile
                center_lat=GEEConfig.BONDOUKOU_CENTER[1], # Utiliser le centre de la région par défaut
                center_lon=GEEConfig.BONDOUKOU_CENTER[0], # ou extraire de l'image si disponible et pertinent
                processing_status=ImageModel.ProcessingStatus.PENDING, # Statut initial
                requested_by_id=user_id,
                # Les champs ndvi_data, processed_at etc. seront remplis par la tâche Celery
            )
            print(f"Image record {image_record.id} créé avec statut PENDING pour GEE ID {gee_asset_id}.")

            # Lancement de la tâche Celery pour le traitement asynchrone
            process_gee_image_task.delay(image_record.id)
            print(f"Tâche Celery process_gee_image_task lancée pour l'image ID: {image_record.id}")

            return image_record

        except ee.EEException as e:
            print(f"Erreur GEE lors de la récupération des métadonnées pour {gee_asset_id}: {e}")
            # Pas de image_record créé ici si getInfo() échoue, donc pas de statut d'erreur à sauvegarder sur un objet.
            return None
        except Exception as e:
            print(f"Erreur générale lors de la création de l'enregistrement image pour {gee_asset_id}: {e}")
            # Si image_record a été créé avant l'erreur (peu probable ici, mais par sécurité)
            if 'image_record' in locals() and image_record.id:
                image_record.processing_status = ImageModel.ProcessingStatus.ERROR
                image_record.processing_error = f"Erreur de création initiale: {str(e)}"
                image_record.save()
            return None