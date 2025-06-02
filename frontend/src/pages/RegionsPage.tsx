import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  MagnifyingGlassIcon,
  MapPinIcon,
  UserGroupIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { regionsAPI } from '../services/api';

interface Region {
  id: number;
  name: string;
  description: string;
  status: 'active' | 'inactive';
  created_at: string;
  agent_count: number;
  alert_count: number;
  detection_count: number;
}

export const RegionsPage: React.FC = () => {
  const { user, hasAuthority } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedRegion, setSelectedRegion] = useState<Region | null>(null);

  const queryClient = useQueryClient();

  // Requête pour les régions
  const { data: regions, isLoading } = useQuery({
    queryKey: ['regions'],
    queryFn: () => regionsAPI.getRegions(),
  });

  // Mutation pour mettre à jour le statut d'une région
  const updateRegionStatus = useMutation({
    mutationFn: (data: { id: number; status: string }) =>
      regionsAPI.updateRegionStatus(data.id, data.status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['regions'] });
    },
  });

  // Filtrage des régions
  const filteredRegions = React.useMemo(() => {
    if (!regions?.data) return [];

    return regions.data
      .filter((region: Region) => {
        const matchesSearch = 
          region.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          region.description.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesStatus = statusFilter === 'all' || region.status === statusFilter;
        return matchesSearch && matchesStatus;
      })
      .sort((a: Region, b: Region) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
  }, [regions?.data, searchTerm, statusFilter]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-forest-green text-white';
      case 'inactive':
        return 'bg-alert-red text-white';
      default:
        return 'bg-gray-200 text-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-semibold text-night-blue">
          Régions
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Gestion des régions et de leurs activités
        </p>
      </div>

      {/* Filtres et recherche */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Rechercher une région..."
              className="input-field pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
          </div>
        </div>
        <div className="flex gap-4">
          <select
            className="input-field"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">Tous les statuts</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      {/* Liste des régions */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-night-blue"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRegions.map((region: Region) => (
            <div key={region.id} className="card">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-medium text-night-blue">
                    {region.name}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {region.description}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(region.status)}`}>
                  {region.status === 'active' ? 'Active' : 'Inactive'}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-gray-500">
                    <UserGroupIcon className="h-4 w-4" />
                    <span className="text-sm">{region.agent_count}</span>
                  </div>
                  <span className="text-xs text-gray-400">Agents</span>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-gray-500">
                    <ExclamationTriangleIcon className="h-4 w-4" />
                    <span className="text-sm">{region.alert_count}</span>
                  </div>
                  <span className="text-xs text-gray-400">Alertes</span>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center gap-1 text-gray-500">
                    <MapPinIcon className="h-4 w-4" />
                    <span className="text-sm">{region.detection_count}</span>
                  </div>
                  <span className="text-xs text-gray-400">Détections</span>
                </div>
              </div>

              {/* Actions */}
              {hasAuthority('Responsable Régional') && (
                <div className="flex gap-2">
                  {region.status === 'active' ? (
                    <button
                      onClick={() => updateRegionStatus.mutate({ id: region.id, status: 'inactive' })}
                      className="btn-secondary text-sm flex-1 flex items-center justify-center gap-2"
                    >
                      <XCircleIcon className="h-4 w-4" />
                      Désactiver
                    </button>
                  ) : (
                    <button
                      onClick={() => updateRegionStatus.mutate({ id: region.id, status: 'active' })}
                      className="btn-primary text-sm flex-1 flex items-center justify-center gap-2"
                    >
                      <CheckCircleIcon className="h-4 w-4" />
                      Activer
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Message si aucune région */}
      {!isLoading && filteredRegions.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Aucune région trouvée</p>
        </div>
      )}
    </div>
  );
}; 