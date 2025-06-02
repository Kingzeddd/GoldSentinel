import ee
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from django.utils import timezone

from gee.config import GEEConfig
from image.models.image_model import ImageModel
from region.models.region_model import RegionModel


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

    def process_image_complete(self, gee_asset_id: str, user_id: int = None) -> Optional[ImageModel]:
        """
        Traitement complet d'une image : calcul indices + sauvegarde DB

        Args:
            gee_asset_id: ID asset Google Earth Engine
            user_id: ID utilisateur ayant demandé l'analyse

        Returns:
            Instance ImageModel créée ou None si erreur
        """
        try:
            # VÉRIFICATION SI IMAGE EXISTE DÉJÀ
            existing_image = ImageModel.objects.filter(gee_asset_id=gee_asset_id).first()

            if existing_image:
                print(f"Image {gee_asset_id} déjà traitée, récupération...")
                return existing_image

            # Récupération métadonnées image
            image_ee = ee.Image(gee_asset_id)
            properties = image_ee.getInfo()['properties']

            # Récupération région Bondoukou (à créer si n'existe pas)
            bondoukou_region, created = RegionModel.objects.get_or_create(
                name='BONDOUKOU',
                defaults={
                    'code': 'BDK',
                    'area_km2': 12000,
                    'center_lat': 8.0402,
                    'center_lon': -2.8000
                }
            )

            # Création enregistrement image
            image_record = ImageModel.objects.create(
                name=f"Bondoukou_{datetime.fromtimestamp(properties['system:time_start'] / 1000).strftime('%Y%m%d')}",
                region=bondoukou_region,
                capture_date=datetime.fromtimestamp(properties['system:time_start'] / 1000).date(),
                satellite_source='SENTINEL2',
                cloud_coverage=properties.get('CLOUDY_PIXEL_PERCENTAGE', 0),
                resolution=10,
                gee_asset_id=gee_asset_id,
                gee_collection=GEEConfig.SENTINEL2_COLLECTION,
                center_lat=8.0402,
                center_lon=-2.8000,
                processing_status='PROCESSING',
                requested_by_id=user_id
            )

            # Calcul indices spectraux
            indices_data = self.calculate_spectral_indices(gee_asset_id)

            if indices_data:
                # Mise à jour avec indices calculés
                image_record.ndvi_data = indices_data.get('ndvi_data')
                image_record.ndwi_data = indices_data.get('ndwi_data')
                image_record.ndti_data = indices_data.get('ndti_data')

                # Stockage moyennes pour accès rapide
                image_record.ndvi_mean = indices_data.get('ndvi_data', {}).get('mean')
                image_record.ndwi_mean = indices_data.get('ndwi_data', {}).get('mean')
                image_record.ndti_mean = indices_data.get('ndti_data', {}).get('mean')

                image_record.processing_status = 'COMPLETED'
                image_record.processed_at = timezone.now()
            else:
                image_record.processing_status = 'ERROR'
                image_record.processing_error = "Erreur calcul indices spectraux"

            image_record.save()
            return image_record

        except Exception as e:
            print(f"Erreur traitement image complète: {e}")
            if 'image_record' in locals():
                image_record.processing_status = 'ERROR'
                image_record.processing_error = str(e)
                image_record.save()
            return None