import axios from 'axios';
import { authService } from './auth.service'; // Corrected import

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface Image {
  id: number;
  name: string;
  capture_date: string;
  satellite_source: string;
  cloud_coverage: number;
  resolution: number;
  gee_asset_id: string;
  gee_collection: string;
  processing_status: string;
  processed_at: string | null;
  processing_error: string | null;
  ndvi_mean: number | null;
  ndwi_mean: number | null;
  ndti_mean: number | null;
  region: number;
  region_name: string;
  requested_by: number | null;
  requested_by_name: string | null;
  center_lat: number;
  center_lon: number;
  created_at: string;
}

class ImageService {
  private getHeaders() {
    const token = authService.getAccessToken(); // Corrected method name
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getImages(params?: any): Promise<{ count: number; results: Image[] }> {
    const response = await axios.get(`${API_URL}/images/`, {
      headers: this.getHeaders(),
      params,
    });
    return response.data;
  }

  async getImage(id: number): Promise<Image> {
    const response = await axios.get(`${API_URL}/images/${id}/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getRecentImages(): Promise<{ count: number; results: Image[] }> {
    const response = await axios.get(`${API_URL}/images/recent/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async runAnalysis(monthsBack: number = 3): Promise<{
    success: boolean;
    message: string;
    data?: {
      images_processed: number;
      detections_found: number;
      alerts_generated: number;
      investigations_created: number;
      analysis_date: string;
    };
    errors?: string[];
  }> {
    const response = await axios.post(
      `${API_URL}/analysis/run/`,
      { months_back: monthsBack },
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}

export default new ImageService(); 