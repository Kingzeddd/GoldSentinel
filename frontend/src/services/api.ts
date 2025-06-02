import axios from 'axios';
// import { setAuthHeader } from './authHelpers'; // Assurez-vous que ce helper existe et est correct

const API_URL = '/api/v1'; // Base URL pour votre API
const BACKEND_BASE_URL = 'http://localhost:8000'; // URL de base du backend

// Instance Axios configurée
const api = axios.create({
  baseURL: API_URL,
});

// Ajoutez un intercepteur de requête pour inclure le token JWT
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Ajoutez un intercepteur de réponse pour gérer les tokens expirés ou invalides
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si l'erreur est 401 Unauthorized et qu'il ne s'agit pas de la requête de rafraîchissement de token
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const response = await authAPI.refreshToken({ refresh: refreshToken });
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          // Réessayez la requête originale avec le nouveau token
          api.defaults.headers.common['Authorization'] = `Bearer ${access}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Si le rafraîchissement échoue, déconnectez l'utilisateur
          console.error('Impossible de rafraîchir le token', refreshError);
          // Déconnexion - à implémenter dans AuthContext
          // logout(); 
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          // Rediriger vers la page de connexion
          window.location.href = '/login'; 
        }
      } else {
         // Si pas de refresh token, rediriger vers la page de connexion
         // logout(); 
         window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// ---------- APIs par fonctionnalité ----------

// API d'Authentification
export const authAPI = {
  login: (credentials: any) => axios.post(`${BACKEND_BASE_URL}/api/v1/auth/token/`, { email: credentials.username, password: credentials.password }), // Correction ici, utilisez axios direct avec l'URL complète
  refreshToken: (token: { refresh: string }) => api.post('/auth/token/refresh/', token),
  getProfile: () => api.get('/account/profile/'),
  getRecentImages: () => api.get('/images/'),
};

// API Images
export const imagesAPI = {
  getAll: (params?: any) => api.get('/images/', { params }),
  getById: (id: number) => api.get(`/images/${id}/`),
  create: (data: FormData) => api.post('/images/', data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  update: (id: number, data: FormData) => api.patch(`/images/${id}/`, data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  delete: (id: number) => api.delete(`/images/${id}/`),
};

// API Detections
export const detectionsAPI = {
  getAll: (params?: any) => api.get('/detections/', { params }),
  getById: (id: number) => api.get(`/detections/${id}/`),
  getRecentDetections: () => api.get('/detections/'),
  // Ajoutez d'autres endpoints si nécessaire (créer, mettre à jour, supprimer)
};

// API Alerts
export const alertsAPI = {
  getAll: (params?: any) => api.get('/alerts/', { params }),
  getById: (id: number) => api.get(`/alerts/${id}/`),
  getCriticalAlerts: () => api.get('/alerts/', { params: { status: 'critical' } }),
  // Ajoutez d'autres endpoints si nécessaire
};

// API Rapports
export const reportsAPI = {
  getAll: (params?: any) => api.get('/reports/', { params }),
  getById: (id: number) => api.get(`/reports/${id}/`),
  submitReport: (data: any) => api.post('/reports/submit/', data), // Exemple, à adapter
};

// API Investigations
export const investigationsAPI = {
  getAll: (params?: any) => api.get('/investigations/', { params }),
  getById: (id: number) => api.get(`/investigations/${id}/`),
  assignAgent: (id: number, agentId: number) => api.post(`/investigations/${id}/assign/`, { agent_id: agentId }),
  updateStatus: (id: number, status: string) => api.patch(`/investigations/${id}/`, { status }),
  submitReport: (id: number, reportData: any) => api.post(`/investigations/${id}/submit_report/`, reportData), // Exemple, à adapter
  getRecentInvestigations: () => api.get('/investigations/'),
};

// API Régions
export const regionsAPI = {
  getAll: (params?: any) => api.get('/regions/', { params }),
  getById: (id: number) => api.get(`/regions/${id}/`),
  updateStatus: (id: number, status: string) => api.patch(`/regions/${id}/`, { status }), // Exemple, à adapter
};

// API Analyse (Exemple)
export const analysisAPI = {
  requestAnalysis: (data: any) => api.post('/analysis/request/', data), // Exemple, à adapter
};

// API Statistiques (Exemple)
export const statsAPI = {
  getSummary: () => api.get('/stats/summary/'), // Exemple, à adapter
};

// API Compte Utilisateur (Exemple)
export const accountAPI = {
  getProfile: () => api.get('/account/profile/'),
  updateProfile: (data: any) => api.put('/account/profile/', data), // Utilisez PUT pour la mise à jour complète ou PATCH pour partielle
  changePassword: (data: any) => api.post('/account/change-password/', data),
};

// Exportez l'instance configurée si vous avez besoin de l'utiliser directement
export default api; 