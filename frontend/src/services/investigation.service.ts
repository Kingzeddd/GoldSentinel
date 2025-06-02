import axios from 'axios';
import { authService } from './auth.service'; // Corrected import

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface Investigation {
  id: number;
  detection: number;
  detection_info: {
    id: number;
    type: string;
    confidence_score: number;
    area_hectares: number;
    detection_date: string;
  };
  target_coordinates: string;
  access_instructions: string;
  assigned_to: number | null;
  assigned_to_name: string | null;
  status: string;
  status_display: string;
  result: string | null;
  result_display: string | null;
  field_notes: string;
  investigation_date: string | null;
  created_at: string;
  updated_at: string;
  agents: Array<{
    id: number;
    name: string;
  }>;
  region: string;
}

export interface Agent {
  id: number;
  full_name: string;
  identifier: string;
  email: string;
  active_investigations_count: number;
  pending_investigations_count: number;
  total_workload: number;
  availability_status: string;
  last_login: string | null;
}

export interface InvestigationFilters {
  status?: string;
  agent?: string;
  region?: string;
  dateRange?: {
    start: string;
    end: string;
  };
}

class InvestigationService {
  private getHeaders() {
    const token = authService.getAccessToken(); // Corrected method name
    return {
      Authorization: `Bearer ${token}`,
    };
  }

  async getInvestigations(params?: any): Promise<{ count: number; results: Investigation[] }> {
    const response = await axios.get(`${API_URL}/investigations/`, {
      headers: this.getHeaders(),
      params,
    });
    return response.data;
  }

  async getInvestigation(id: number): Promise<Investigation> {
    const response = await axios.get(`${API_URL}/investigations/${id}/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getPendingInvestigations(): Promise<{ count: number; results: Investigation[] }> {
    const response = await axios.get(`${API_URL}/investigations/pending/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getMyInvestigations(): Promise<{ count: number; results: Investigation[] }> {
    const response = await axios.get(`${API_URL}/investigations/assigned-to-me/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async getAvailableAgents(): Promise<{
    count: number;
    agents: Agent[];
    summary: {
      total_agents: number;
      available_agents: number;
      busy_agents: number;
      overloaded_agents: number;
    };
  }> {
    const response = await axios.get(`${API_URL}/investigations/available-agents/`, {
      headers: this.getHeaders(),
    });
    return response.data;
  }

  async assignInvestigation(
    id: number,
    assignedTo: number,
    priority: string = 'MEDIUM',
    notes: string = ''
  ): Promise<{
    success: boolean;
    message: string;
    data: Investigation;
    agent_info: {
      name: string;
      new_workload: number;
    };
    warning?: string;
  }> {
    const response = await axios.patch(
      `${API_URL}/investigations/${id}/assign/`,
      {
        assigned_to: assignedTo,
        priority,
        notes,
      },
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async submitResult(
    id: number,
    result: string,
    fieldNotes: string,
    investigationDate?: string
  ): Promise<{
    message: string;
    data: Investigation;
  }> {
    const response = await axios.patch(
      `${API_URL}/investigations/${id}/result/`,
      {
        result,
        field_notes: fieldNotes,
        investigation_date: investigationDate,
      },
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  // Nouvelles méthodes pour le filtrage et la pagination

  async getFilteredInvestigations(
    filters: InvestigationFilters,
    page: number = 0,
    pageSize: number = 20
  ): Promise<{ count: number; results: Investigation[] }> {
    const params = {
      page: page + 1, // L'API utilise une pagination 1-based
      page_size: pageSize,
      ...filters,
    };

    const response = await axios.get(`${API_URL}/investigations/`, {
      headers: this.getHeaders(),
      params,
    });
    return response.data;
  }

  async getInvestigationRegions(): Promise<string[]> {
    const response = await axios.get(`${API_URL}/investigations/`, {
      headers: this.getHeaders(),
    });
    const investigations = response.data.results;
    return [...new Set(investigations.map((i: Investigation) => i.region))];
  }

  async getInvestigationAgents(): Promise<Array<{ id: number; name: string }>> {
    const response = await axios.get(`${API_URL}/investigations/`, {
      headers: this.getHeaders(),
    });
    const investigations = response.data.results;
    const agents = investigations.flatMap((i: Investigation) => i.agents);
    return [...new Map(agents.map(agent => [agent.id, agent])).values()];
  }
}

export default new InvestigationService(); 