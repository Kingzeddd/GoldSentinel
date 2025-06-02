import axios from 'axios';
import { authService } from './auth.service'; // Corrected import

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface Region {
  id: number;
  name: string;
  code: string;
  area_km2: number;
  center_lat: number;
  center_lon: number;
  monitored_zones: string[];
  authorized_sites: string[];
  protected_zones: string[];
}

class RegionService {
  private getHeaders() {
    const token = authService.getAccessToken(); // Corrected method name
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getRegions(): Promise<Region[]> {
    const response = await axios.get(`${API_URL}/regions/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getRegion(id: number): Promise<Region> {
    const response = await axios.get(`${API_URL}/regions/${id}/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }
}

export default new RegionService(); 