import axios from 'axios';
import authService from './auth.service';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface Detection {
  id: number;
  image: number;
  image_name: string;
  image_capture_date: string;
  region: number;
  region_name: string;
  latitude: number;
  longitude: number;
  detection_type: string;
  confidence_score: number;
  area_hectares: number;
  ndvi_anomaly_score: number;
  ndwi_anomaly_score: number;
  ndti_anomaly_score: number;
  validation_status: string;
  validated_by: number | null;
  validated_by_name: string | null;
  validated_at: string | null;
  detection_date: string;
  algorithm_version: string;
}

class DetectionService {
  private getHeaders() {
    const token = authService.getToken();
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getDetections(params?: any): Promise<{ count: number; results: Detection[] }> {
    const response = await axios.get(`${API_URL}/detections/`, {
      headers: this.getHeaders(),
      params,
    });
    return response.data;
  }

  async getDetection(id: number): Promise<Detection> {
    const response = await axios.get(`${API_URL}/detections/${id}/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getHighConfidenceDetections(): Promise<{ count: number; results: Detection[] }> {
    const response = await axios.get(`${API_URL}/detections/high-confidence/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async validateDetection(id: number, validationStatus: string): Promise<Detection> {
    const response = await axios.patch(
      `${API_URL}/detections/${id}/validate/`,
      { validation_status: validationStatus },
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async deleteDetection(id: number): Promise<void> {
    await axios.delete(`${API_URL}/detections/${id}/`, {
      headers: this.getHeaders(),
    });
  }
}

export default new DetectionService(); 