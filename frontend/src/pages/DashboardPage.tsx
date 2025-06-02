import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  PhotoIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  DocumentTextIcon,
  UserGroupIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { imagesAPI, detectionsAPI, alertsAPI, investigationsAPI } from '../services/api';

interface StatCard {
  title: string;
  value: number;
  icon: React.ElementType;
  color: string;
}

export const DashboardPage: React.FC = () => {
  const { user, hasAuthority } = useAuth();

  // Requêtes pour les données
  const { data: imagesData } = useQuery({
    queryKey: ['recent-images'],
    queryFn: () => imagesAPI.getRecentImages(),
  });

  const { data: detectionsData } = useQuery({
    queryKey: ['recent-detections'],
    queryFn: () => detectionsAPI.getRecentDetections(),
  });

  const { data: alertsData } = useQuery({
    queryKey: ['critical-alerts'],
    queryFn: () => alertsAPI.getCriticalAlerts(),
  });

  const { data: investigationsData } = useQuery({
    queryKey: ['recent-investigations'],
    queryFn: () => investigationsAPI.getRecentInvestigations(),
  });

  // Statistiques en fonction du rôle
  const getStats = (): StatCard[] => {
    const stats: StatCard[] = [];

    // Statistiques communes à tous les rôles
    stats.push({
      title: 'Images analysées',
      value: imagesData?.data?.length || 0,
      icon: PhotoIcon,
      color: 'bg-night-blue',
    });

    // Statistiques pour Responsable Régional et Administrateur
    if (hasAuthority('Responsable Régional') || hasAuthority('Administrateur')) {
      stats.push(
        {
          title: 'Détections',
          value: detectionsData?.data?.length || 0,
          icon: ChartBarIcon,
          color: 'bg-gold',
        },
        {
          title: 'Alertes critiques',
          value: alertsData?.data?.length || 0,
          icon: ExclamationTriangleIcon,
          color: 'bg-alert-red',
        },
        {
          title: 'Investigations en cours',
          value: investigationsData?.data?.length || 0,
          icon: DocumentTextIcon,
          color: 'bg-forest-green',
        }
      );
    }

    // Statistiques pour Agent Terrain
    if (hasAuthority('Agent Terrain')) {
      stats.push(
        {
          title: 'Mes investigations',
          value: investigationsData?.data?.filter(inv => inv.assigned_to === user?.id).length || 0,
          icon: UserGroupIcon,
          color: 'bg-forest-green',
        },
        {
          title: 'Détections en attente',
          value: detectionsData?.data?.filter(det => det.status === 'pending').length || 0,
          icon: ClockIcon,
          color: 'bg-gold',
        }
      );
    }

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