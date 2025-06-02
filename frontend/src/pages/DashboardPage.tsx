import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ExclamationTriangleIcon,
  ChartBarIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ClockIcon,
  BanknotesIcon, // For financial risk
  ShieldCheckIcon, // For accuracy rate
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { imagesAPI, detectionsAPI, alertsAPI, investigationsAPI } from '../services/api'; // Keep existing imports for now
// Corrected import for DashboardStats type
import statsService from '../services/stats.service';
import type { DashboardStats } from '../services/stats.service';

interface StatCard {
  title: string;
  value: number;
  icon: React.ElementType;
  color: string;
}

export const DashboardPage: React.FC = () => {
  const { user, hasAuthority } = useAuth();

  // Fetch dashboard statistics
  const { data: dashboardStatsData, isLoading: isLoadingStats } = useQuery<DashboardStats, Error>({
    queryKey: ['dashboardStats'],
    queryFn: () => statsService.getDashboardStats(),
  });

  // Existing data queries - keep them for now, will remove if statsService provides all needed data
  const { data: imagesData } = useQuery({
    queryKey: ['recent-images'],
    queryFn: () => imagesAPI.getRecentImages(), // This might be replaceable by dashboardStatsData
  });

  const { data: detectionsData } = useQuery({ // This might be replaceable
    queryKey: ['recent-detections'],
    queryFn: () => detectionsAPI.getRecentDetections(),
  });

  const { data: alertsData } = useQuery({ // This might be replaceable
    queryKey: ['critical-alerts'],
    queryFn: () => alertsAPI.getCriticalAlerts(),
  });

  const { data: investigationsData } = useQuery({ // This might be replaceable
    queryKey: ['recent-investigations'],
    queryFn: () => investigationsAPI.getRecentInvestigations(),
  });

  // Statistiques en fonction du rôle
  const getStats = (): StatCard[] => {
    if (isLoadingStats || !dashboardStatsData) {
      // Return a loading state or empty array if data is not yet available
      return [];
    }

    const stats: StatCard[] = [];
    const {
      total_detections,
      active_alerts,
      pending_investigations,
      total_financial_risk,
      // analysis_period_days, // Not directly used in cards
      // last_analysis_date, // Not directly used in cards
      accuracy_rate,
      // high_confidence_detections, // Could be a new card
      // detections_trend, // For charts, not cards
      // alerts_by_level, // Could be detailed view, not simple card
      // affected_zones, // For map or detailed view
    } = dashboardStatsData;

    // Common stats for all roles that have access to the dashboard
    // Assuming 'Images analysées' can be derived or is a separate metric.
    // For now, let's use a placeholder or remove if not in dashboardStatsData.
    // If total_detections implies images were analyzed, we can use it.
    // Let's assume total_detections is a good general metric.
    stats.push({
      title: 'Total Détections',
      value: total_detections,
      icon: ChartBarIcon, // Using ChartBarIcon for detections
      color: 'bg-night-blue',
    });

    // Statistiques pour Responsable Régional et Administrateur
    if (hasAuthority('Responsable Régional') || hasAuthority('Administrateur')) {
      stats.push(
        {
          title: 'Alertes Actives',
          value: active_alerts,
          icon: ExclamationTriangleIcon,
          color: 'bg-alert-red',
        },
        {
          title: 'Investigations en Attente',
          value: pending_investigations,
          icon: DocumentTextIcon,
          color: 'bg-forest-green',
        },
        {
          title: 'Risque Financier Total (FCFA)',
          value: total_financial_risk, // Assuming this is a numerical value
          icon: BanknotesIcon,
          color: 'bg-yellow-500', // Example color
        },
        {
          title: 'Taux de Précision',
          value: parseFloat((accuracy_rate * 100).toFixed(2)), // Format as percentage
          icon: ShieldCheckIcon,
          color: 'bg-green-500', // Example color
        }
      );
    }

    // Statistiques pour Agent Terrain
    // The new stats endpoint does not seem to provide agent-specific "Mes investigations"
    // or "Détections en attente" (pending for *that* agent).
    // We might need to keep investigationsData and detectionsData for these specific cards,
    // or adjust the backend to provide this level of detail in dashboardStats.
    if (hasAuthority('Agent Terrain')) {
      stats.push(
        {
          title: 'Mes investigations', // This specific stat might not be in dashboardStatsData
          value: investigationsData?.data?.filter((inv: any) => inv.assigned_to === user?.id).length || 0,
          icon: UserGroupIcon, // Changed from UsersIcon to UserGroupIcon as per original
          color: 'bg-forest-green',
        },
        {
          title: 'Détections en attente', // This specific stat might not be in dashboardStatsData
          value: detectionsData?.data?.filter((det: any) => det.status === 'pending').length || 0,
          icon: ClockIcon,
          color: 'bg-gold',
        }
      );
    }
    // Add other stats from dashboardStatsData as needed, for example:
    // stats.push({
    //   title: 'Images Analysées', (If available, or map from another source)
    //   value: imagesData?.data?.length || 0, // Placeholder, needs to be confirmed
    //   icon: PhotoIcon,
    //   color: 'bg-sky-blue',
    // });

    return stats;
  };

  return (
    <div className="space-y-6">
      {/* En-tête avec informations utilisateur */}
      <div>
        <h1 className="text-2xl font-heading font-semibold text-night-blue">
          Tableau de bord
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Bienvenue, {user?.full_name} - {user?.job_title}
        </p>
        <p className="text-sm text-gray-500">
          Région : {user?.authorized_region}
        </p>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {getStats().map((stat, index) => (
          <div key={index} className="card">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.color}`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">{stat.title}</p>
                <p className="text-2xl font-semibold text-night-blue">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Alertes critiques (Responsable Régional et Administrateur uniquement) */}
      {(hasAuthority('Responsable Régional') || hasAuthority('Administrateur')) && (
        <div className="card">
          <h2 className="text-lg font-medium text-night-blue mb-4">Alertes critiques</h2>
          {alertsData?.data?.length ? (
            <div className="space-y-4">
              {alertsData.data.map((alert: any) => (
                <div key={alert.id} className="bg-red-50 p-4 rounded-lg">
                  <h3 className="font-medium text-red-800">{alert.title}</h3>
                  <p className="text-sm text-red-600 mt-1">{alert.description}</p>
                  <p className="text-xs text-red-500 mt-2">
                    {new Date(alert.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">Aucune alerte critique</p>
          )}
        </div>
      )}

      {/* Images récentes */}
      <div className="card">
        <h2 className="text-lg font-medium text-night-blue mb-4">Images récentes</h2>
        {imagesData?.data?.length ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {imagesData.data.map((image: any) => (
              <div key={image.id} className="relative aspect-square">
                <img
                  src={image.url}
                  alt={image.filename}
                  className="w-full h-full object-cover rounded-lg"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-2 rounded-b-lg">
                  <p className="text-xs truncate">{image.filename}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">Aucune image récente</p>
        )}
      </div>
    </div>
  );
}; 