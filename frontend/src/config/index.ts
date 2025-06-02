export const API_URL = import.meta.env.VITE_API_URL;
export const APP_NAME = import.meta.env.VITE_APP_NAME;
export const APP_VERSION = import.meta.env.VITE_APP_VERSION;

// Configuration des routes
export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  INVESTIGATIONS: '/investigations',
  ALERTS: '/alerts',
  PROFILE: '/profile',
};

// Configuration des statuts
export const STATUS = {
  INVESTIGATION: {
    PENDING: 'PENDING',
    ASSIGNED: 'ASSIGNED',
    IN_PROGRESS: 'IN_PROGRESS',
    COMPLETED: 'COMPLETED',
  },
  ALERT: {
    ACTIVE: 'ACTIVE',
    ACKNOWLEDGED: 'ACKNOWLEDGED',
    RESOLVED: 'RESOLVED',
    FALSE_ALARM: 'FALSE_ALARM',
  },
};

// Configuration des niveaux d'alerte
export const ALERT_LEVELS = {
  CRITICAL: 'CRITICAL',
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW',
};

// Configuration des types de détection
export const DETECTION_TYPES = {
  MINING_SITE: 'MINING_SITE',
  WATER_POLLUTION: 'WATER_POLLUTION',
  DEFORESTATION: 'DEFORESTATION',
  SOIL_DISTURBANCE: 'SOIL_DISTURBANCE',
}; 