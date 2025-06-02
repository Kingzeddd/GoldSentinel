import axios from 'axios';
import authService from './auth.service';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface DashboardStats {
  total_detections: number;
  active_alerts: number;
  pending_investigations: number;
  total_financial_risk: number;
  analysis_period_days: number;
  last_analysis_date: string;
  accuracy_rate: number;
  high_confidence_detections: number;
  detections_trend: Array<{
    date: string;
    count: number;
  }>;
  alerts_by_level: Record<string, number>;
  affected_zones: Array<{
    zone: string;
    detections: number;
  }>;
}

export interface ExecutiveSummary {
  period: string;
  key_metrics: {
    total_detections: number;
    critical_situations: number;
    estimated_financial_impact_fcfa: number;
    system_accuracy_percent: number;
    active_field_investigations: number;
  };
  recommendations: string[];
  next_actions: string[];
}

export interface DetectionTrends {
  period_days: number;
  daily_detections: Array<{
    day: string;
    count: number;
  }>;
  average_confidence: number;
  high_confidence_count: number;
  trend_analysis: string;
}

export interface FinancialImpact {
  total_estimated_loss_fcfa: number;
  total_affected_area_hectares: number;
  average_cost_per_hectare_fcfa: number;
  breakdown_by_risk_level: Array<{
    risk_level: string;
    count: number;
    total_amount: number;
    avg_amount: number;
  }>;
  economic_context: {
    ministry_annual_estimate_fcfa: number;
    our_detection_percentage: number;
  };
}

class StatsService {
  private getHeaders() {
    const token = authService.getToken();
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getDashboardStats(): Promise<DashboardStats> {
    const response = await axios.get(`${API_URL}/stats/dashboard/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getExecutiveSummary(): Promise<ExecutiveSummary> {
    const response = await axios.get(`${API_URL}/stats/summary/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getDetectionTrends(days: number = 30): Promise<DetectionTrends> {
    const response = await axios.get(`${API_URL}/stats/detection-trends/`, {
      headers: this.getHeaders(),
      params: { days },
    });
    return response.data;
  }

  async getFinancialImpact(): Promise<FinancialImpact> {
    const response = await axios.get(`${API_URL}/stats/financial-impact/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }
}

export default new StatsService(); 