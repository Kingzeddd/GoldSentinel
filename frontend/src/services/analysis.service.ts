import axios from 'axios';
import { authService } from './auth.service'; // Corrected import

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface AnalysisResult {
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
}

class AnalysisService {
  private getHeaders() {
    const token = authService.getAccessToken(); // Corrected method name
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async runAnalysis(monthsBack: number = 3): Promise<AnalysisResult> {
    const response = await axios.post(
      `${API_URL}/analysis/run/`,
      { months_back: monthsBack },
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}

export default new AnalysisService(); 