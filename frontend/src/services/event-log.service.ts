import axios from 'axios';
import authService from './auth.service';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface EventLog {
  id: number;
  event_type: string;
  event_type_display: string;
  message: string;
  user: number | null;
  user_name: string | null;
  detection: number | null;
  detection_info: {
    id: number;
    type: string;
    confidence: number;
  } | null;
  alert: number | null;
  region: number | null;
  metadata: Record<string, any>;
  created_at: string;
  time_since: string;
}

class EventLogService {
  private getHeaders() {
    const token = authService.getToken();
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getEventLogs(params?: any): Promise<{ count: number; results: EventLog[] }> {
    const response = await axios.get(`${API_URL}/events/`, {
      headers: this.getHeaders(),
      params,
    });
    return response.data;
  }

  async getRecentEvents(): Promise<{
    count: number;
    period: string;
    results: EventLog[];
  }> {
    const response = await axios.get(`${API_URL}/events/recent/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getEventsByType(): Promise<{
    total_events: number;
    by_type: Array<{
      event_type: string;
      label: string;
      count: number;
    }>;
  }> {
    const response = await axios.get(`${API_URL}/events/by-type/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }
}

export default new EventLogService(); 