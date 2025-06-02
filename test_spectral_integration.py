#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration des fonctionnalités spectrales
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gee.services.mining_detection_service import MiningDetectionService
from gee.services.earth_engine_service import EarthEngineService
from image.models.image_model import ImageModel

def test_tensorflow_model():
    """Test du chargement du modèle TensorFlow"""
    print("🧪 Test du modèle TensorFlow...")
    try:
        service = MiningDetectionService()
        if service.model:
            print("✅ Modèle TensorFlow chargé avec succès")
            
            # Test de prédiction avec des données factices
            test_data = {
                'ndvi_data': {'mean': 0.5, 'stddev': 0.1},
                'ndwi_data': {'mean': 0.2, 'stddev': 0.05},
                'ndti_data': {'mean': 0.1, 'stddev': 0.02}
            }
            
            confidence = service._predict_with_tensorflow(test_data)
            print(f"✅ Prédiction test: {confidence:.3f}")
        else:
            print("⚠️ Modèle TensorFlow non chargé")
    except Exception as e:
        print(f"❌ Erreur modèle TensorFlow: {e}")

def test_earth_engine():
    """Test de Google Earth Engine"""
    print("\n🌍 Test de Google Earth Engine...")
    try:
        service = EarthEngineService()
        if service.initialized:
            print("✅ Google Earth Engine initialisé")
            
            # Test de récupération d'images récentes
            images = service.get_recent_images(months_back=1)
            print(f"✅ {len(images)} images trouvées")
        else:
            print("❌ Google Earth Engine non initialisé")
    except Exception as e:
        print(f"❌ Erreur Google Earth Engine: {e}")

def test_spectral_calculation():
    """Test du calcul d'indices spectraux"""
    print("\n📊 Test du calcul d'indices spectraux...")
    try:
        # Récupération d'une image test
        image = ImageModel.objects.filter(
            processing_status='COMPLETED',
            gee_asset_id__isnull=False
        ).first()
        
        if image:
            print(f"✅ Image test trouvée: {image.name}")
            
            service = EarthEngineService()
            if service.initialized:
                # Test génération cartes spectrales
                maps_data = service.generate_spectral_maps(image.gee_asset_id)
                if maps_data:
                    print("✅ Cartes spectrales générées")
                    print(f"   - NDVI: {maps_data.get('ndvi_map_url', 'N/A')[:50]}...")
                    print(f"   - NDWI: {maps_data.get('ndwi_map_url', 'N/A')[:50]}...")
                    print(f"   - NDTI: {maps_data.get('ndti_map_url', 'N/A')[:50]}...")
                else:
                    print("⚠️ Aucune carte spectrale générée")
            else:
                print("⚠️ Google Earth Engine non disponible")
        else:
            print("⚠️ Aucune image test disponible")
    except Exception as e:
        print(f"❌ Erreur calcul spectral: {e}")

def test_detection_integration():
    """Test de l'intégration complète de détection"""
    print("\n🎯 Test de l'intégration de détection...")
    try:
        # Récupération d'une image pour test
        image = ImageModel.objects.filter(
            processing_status='COMPLETED'
        ).first()
        
        if image:
            print(f"✅ Image test: {image.name}")
            
            service = MiningDetectionService()
            detections = service.analyze_for_mining_activity(image)
            
            print(f"✅ Analyse terminée: {len(detections)} détections")
            for detection in detections:
                print(f"   - Score: {detection.confidence_score:.3f}")
                print(f"   - Type: {detection.detection_type}")
                print(f"   - Surface: {detection.area_hectares:.1f} ha")
        else:
            print("⚠️ Aucune image disponible pour test")
    except Exception as e:
        print(f"❌ Erreur intégration détection: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 Test d'intégration des fonctionnalités spectrales")
    print("=" * 60)
    
    test_tensorflow_model()
    test_earth_engine()
    test_spectral_calculation()
    test_detection_integration()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")

if __name__ == "__main__":
    main()
