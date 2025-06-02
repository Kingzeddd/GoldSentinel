import axios from 'axios';
import authService from './auth.service';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface SpectralMapsData {
  image_id: number;
  image_name: string;
  capture_date: string;
  region: string;
  spectral_maps: {
    ndvi_map_url: string;
    ndwi_map_url: string;
    ndti_map_url: string;
    bounds: {
      north: number;
      south: number;
      east: number;
      west: number;
    };
  };
  indices_data: {
    ndvi: {
      mean: number;
      stddev: number;
      computed_at: string;
    };
    ndwi: {
      mean: number;
      stddev: number;
      computed_at: string;
    };
    ndti: {
      mean: number;
      stddev: number;
      computed_at: string;
    };
  };
}

export interface IndicesData {
  image_id: number;
  ndvi_data: {
    mean: number;
    stddev: number;
    computed_at: string;
  };
  ndwi_data: {
    mean: number;
    stddev: number;
    computed_at: string;
  };
  ndti_data: {
    mean: number;
    stddev: number;
    computed_at: string;
  };
  ndvi_mean: number;
  ndwi_mean: number;
  ndti_mean: number;
  processing_status: string;
  processed_at: string;
}

export interface TrendsData {
  region_id: number;
  period: {
    start: string;
    end: string;
  };
  trends: Array<{
    date: string;
    ndvi_mean: number;
    ndwi_mean: number;
    ndti_mean: number;
    image_id: number;
  }>;
}

class SpectralService {
  private getHeaders() {
    const token = authService.getToken();
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getSpectralMaps(imageId: number): Promise<SpectralMapsData> {
    const response = await axios.get(
      `${API_URL}/spectral/maps/${imageId}/`,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async getIndicesData(imageId: number): Promise<IndicesData> {
    const response = await axios.get(
      `${API_URL}/spectral/indices/${imageId}/`,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async getIndicesTrends(regionId: number): Promise<TrendsData> {
    const response = await axios.get(
      `${API_URL}/spectral/trends/${regionId}/`,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  // Méthode utilitaire pour analyser les anomalies
  analyzeAnomalies(currentData: IndicesData, referenceData?: IndicesData) {
    if (!referenceData) {
      return {
        ndvi_anomaly: 0,
        ndwi_anomaly: 0,
        ndti_anomaly: 0,
        overall_risk: 'low'
      };
    }

    const ndvi_anomaly = Math.abs(currentData.ndvi_mean - referenceData.ndvi_mean);
    const ndwi_anomaly = Math.abs(currentData.ndwi_mean - referenceData.ndwi_mean);
    const ndti_anomaly = Math.abs(currentData.ndti_mean - referenceData.ndti_mean);

    // Calcul du risque global
    const anomaly_score = (ndvi_anomaly * 0.4) + (ndwi_anomaly * 0.3) + (ndti_anomaly * 0.3);
    
    let overall_risk = 'low';
    if (anomaly_score > 0.4) overall_risk = 'high';
    else if (anomaly_score > 0.2) overall_risk = 'medium';

    return {
      ndvi_anomaly,
      ndwi_anomaly,
      ndti_anomaly,
      anomaly_score,
      overall_risk
    };
  }

  // Méthode pour interpréter les valeurs d'indices
  interpretIndex(value: number, indexType: 'ndvi' | 'ndwi' | 'ndti') {
    switch (indexType) {
      case 'ndvi':
        if (value > 0.6) return { status: 'excellent', description: 'Végétation très dense' };
        if (value > 0.4) return { status: 'good', description: 'Végétation dense' };
        if (value > 0.2) return { status: 'moderate', description: 'Végétation modérée' };
        if (value > 0) return { status: 'poor', description: 'Végétation clairsemée' };
        return { status: 'critical', description: 'Absence de végétation' };

      case 'ndwi':
        if (value > 0.3) return { status: 'high', description: 'Forte présence d\'eau' };
        if (value > 0.1) return { status: 'moderate', description: 'Présence d\'eau modérée' };
        if (value > -0.1) return { status: 'low', description: 'Faible humidité' };
        return { status: 'dry', description: 'Zone sèche' };

      case 'ndti':
        if (value > 0.2) return { status: 'disturbed', description: 'Sol fortement perturbé' };
        if (value > 0.1) return { status: 'modified', description: 'Sol modifié' };
        if (value > 0) return { status: 'slight', description: 'Légère modification' };
        return { status: 'natural', description: 'Sol naturel' };

      default:
        return { status: 'unknown', description: 'Valeur inconnue' };
    }
  }
}

export default new SpectralService();
