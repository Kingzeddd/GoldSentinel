import axios from 'axios';
import authService from './auth.service';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  job_title: string;
  institution: string;
  authorized_region: string;
  authorities: string[];
  primary_authority: string;
  is_active: boolean;
}

class ProfileService {
  private getHeaders() {
    const token = authService.getToken();
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getProfile(): Promise<UserProfile> {
    const response = await axios.get(`${API_URL}/account/profile/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await axios.put(
      `${API_URL}/account/profile/`,
      data,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
    const response = await axios.post(
      `${API_URL}/account/change-password/`,
      {
        old_password: oldPassword,
        new_password: newPassword,
      },
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}

export default new ProfileService(); 