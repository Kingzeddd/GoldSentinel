"""
Configuration centralisée des coûts financiers pour détection orpaillage
Basé sur données ministère ivoirien : 3000 milliards FCFA/an
"""
class FinancialSettings:
    """Configuration coûts et paramètres financiers"""

    # Coûts de base par type d'impact (FCFA/hectare)
    BASE_COSTS = {
        'deforestation': 9_300_000,  # 9.3M FCFA/ha - Impact principal orpaillage
        'water_pollution': 5_000_000,  # 5M FCFA/ha - Pollution hydrique
        'soil_degradation': 3_000_000,  # 3M FCFA/ha - Dégradation sols
        'biodiversity_loss': 2_000_000,  # 2M FCFA/ha - Perte biodiversité
    }

    # Coût principal pour orpaillage (déforestation)
    DEFAULT_COST_PER_HECTARE = BASE_COSTS['deforestation']

    # Facteurs multiplicateurs
    DISTANCE_FACTORS = {
        'very_sensitive': 2.0,  # < 1km zones sensibles
        'sensitive': 1.5,  # 1-5km zones sensibles
        'normal': 1.0  # > 5km
    }

    # Seuils niveaux de risque (FCFA)
    RISK_THRESHOLDS = {
        'CRITICAL': 10_000_000,  # 10M FCFA
        'HIGH': 5_000_000,  # 5M FCFA
        'MEDIUM': 1_000_000,  # 1M FCFA
        'LOW': 0  # < 1M FCFA
    }

    # Facteurs intensité selon indices spectraux
    SPECTRAL_FACTORS = {
        'ndvi_severe_threshold': 0.7,  # Déforestation sévère
        'ndvi_factor': 0.5,
        'ndwi_pollution_threshold': 0.5,  # Pollution eau
        'ndwi_factor': 0.3,
        'ndti_disturbance_threshold': 0.6,  # Perturbation sols
        'ndti_factor': 0.2
    }

    @classmethod
    def get_distance_factor(cls, distance_km: float) -> float:
        """Retourne facteur selon distance zones sensibles"""
        if distance_km < 1:
            return cls.DISTANCE_FACTORS['very_sensitive']
        elif distance_km < 5:
            return cls.DISTANCE_FACTORS['sensitive']
        else:
            return cls.DISTANCE_FACTORS['normal']

    @classmethod
    def determine_risk_level_from_loss(cls, estimated_loss: float) -> str:
        """Détermine niveau risque selon perte estimée"""
        if estimated_loss >= cls.RISK_THRESHOLDS['CRITICAL']:
            return 'CRITICAL'
        elif estimated_loss >= cls.RISK_THRESHOLDS['HIGH']:
            return 'HIGH'
        elif estimated_loss >= cls.RISK_THRESHOLDS['MEDIUM']:
            return 'MEDIUM'
        else:
            return 'LOW'