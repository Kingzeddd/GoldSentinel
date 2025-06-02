import axios from 'axios';
import { authService } from './auth.service'; // Corrected import

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface FinancialRisk {
  id: number;
  detection: number;
  detection_info: {
    id: number;
    type: string;
    confidence_score: number;
    coordinates: string;
  };
  area_hectares: number;
  cost_per_hectare: number;
  estimated_loss: number;
  sensitive_zone_distance_km: number;
  occurrence_count: number;
  risk_level: string;
  created_at: string;
}

class FinancialRiskService {
  private getHeaders() {
    const token = authService.getAccessToken(); // Corrected method name
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getFinancialRisks(params?: any): Promise<{ count: number; results: FinancialRisk[] }> {
    const response = await axios.get(`${API_URL}/financial-risks/`, {
      headers: this.getHeaders(),
      params,
    });
    return response.data;
  }

  async getFinancialRisk(id: number): Promise<FinancialRisk> {
    const response = await axios.get(`${API_URL}/financial-risks/${id}/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getHighImpactRisks(): Promise<{
    count: number;
    total_estimated_loss: number;
    results: FinancialRisk[];
  }> {
    const response = await axios.get(`${API_URL}/financial-risks/high-impact/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }
}

export default new FinancialRiskService(); 