import axios from 'axios';
import authService from './auth.service';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface Alert {
  id: number;
  name: string;
  detection: number;
  detection_info: {
    id: number;
    type: string;
    confidence_score: number;
    coordinates: string;
    area_hectares: number;
  };
  region: number;
  region_name: string;
  level: string;
  alert_type: string;
  message: string;
  alert_status: string;
  sent_at: string;
  is_read: boolean;
  assigned_to: number | null;
  assigned_to_name: string | null;
  time_since_created: string;
}

class AlertService {
  private getHeaders() {
    const token = authService.getToken();
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getAlerts(params?: any): Promise<{ count: number; results: Alert[] }> {
    const response = await axios.get(`${API_URL}/alerts/`, {
      headers: this.getHeaders(),
      params,
    });
    return response.data;
  }

  async getAlert(id: number): Promise<Alert> {
    const response = await axios.get(`${API_URL}/alerts/${id}/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getActiveAlerts(): Promise<{ count: number; results: Alert[] }> {
    const response = await axios.get(`${API_URL}/alerts/active/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getCriticalAlerts(): Promise<{ count: number; results: Alert[] }> {
    const response = await axios.get(`${API_URL}/alerts/critical/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async updateAlertStatus(id: number, status: string, assignedTo?: number): Promise<Alert> {
    const response = await axios.patch(
      `${API_URL}/alerts/${id}/status/`,
      { alert_status: status, assigned_to: assignedTo },
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}

export default new AlertService(); 