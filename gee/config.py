import os
import json
import ee
from django.conf import settings


class GEEConfig:
    """Configuration Google Earth Engine"""

    # Chemin vers votre service account key
    SERVICE_ACCOUNT_KEY_PATH = os.path.join(settings.BASE_DIR, 'secrets', 'gee-service-account-key.json')

    # Zone d'intérêt Bondoukou (à ajuster selon vos coordonnées exactes)
    BONDOUKOU_BOUNDS = {
        'lat_min': 7.9,
        'lat_max': 8.2,
        'lon_min': -3.0,
        'lon_max': -2.6
    }

    # Collections satellites
    SENTINEL2_COLLECTION = 'COPERNICUS/S2_SR_HARMONIZED'
    LANDSAT8_COLLECTION = 'LANDSAT/LC08/C02/T1_L2'

    # Paramètres filtrage
    MAX_CLOUD_COVERAGE = 20  # 20% max

    @classmethod
    def initialize_ee(cls):
        """Initialise Earth Engine avec service account"""
        try:
            # Chargement des credentials
            with open(cls.SERVICE_ACCOUNT_KEY_PATH, 'r') as f:
                credentials_info = json.load(f)

            credentials = ee.ServiceAccountCredentials(
                credentials_info['client_email'],
                cls.SERVICE_ACCOUNT_KEY_PATH
            )

            ee.Initialize(credentials)
            return True

        except Exception as e:
            print(f"Erreur initialisation GEE: {e}")
            return False

    @classmethod
    def get_bondoukou_geometry(cls):
        """Retourne la géométrie de la zone Bondoukou"""
        bounds = cls.BONDOUKOU_BOUNDS
        return ee.Geometry.Rectangle([
            bounds['lon_min'], bounds['lat_min'],
            bounds['lon_max'], bounds['lat_max']
        ])