import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  MagnifyingGlassIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  CalendarIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import { reportsAPI } from '../services/api';

interface Report {
  id: number;
  title: string;
  type: 'daily' | 'weekly' | 'monthly' | 'custom';
  created_at: string;
  status: 'generating' | 'completed' | 'failed';
  file_url?: string;
  summary: {
    total_images: number;
    total_detections: number;
    total_alerts: number;
    total_investigations: number;
  };
  period: {
    start_date: string;
    end_date: string;
  };
}

export const ReportsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const { data: reports, isLoading } = useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsAPI.getReports(),
  });

  const filteredReports = React.useMemo(() => {
    if (!reports?.data) return [];

    return reports.data
      .filter((report: Report) => {
        const matchesSearch = 
          report.title.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = typeFilter === 'all' || report.type === typeFilter;
        const matchesStatus = statusFilter === 'all' || report.status === statusFilter;
        return matchesSearch && matchesType && matchesStatus;
      })
      .sort((a: Report, b: Report) => {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
  }, [reports?.data, searchTerm, typeFilter, statusFilter]);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'daily':
        return 'bg-forest-green text-white';
      case 'weekly':
        return 'bg-gold text-white';
      case 'monthly':
        return 'bg-night-blue text-white';
      case 'custom':
        return 'bg-gray-600 text-white';
      default:
        return 'bg-gray-200 text-gray-700';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'generating':
        return 'bg-gold text-white';
      case 'completed':
        return 'bg-forest-green text-white';
      case 'failed':
        return 'bg-alert-red text-white';
      default:
        return 'bg-gray-200 text-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-semibold text-night-blue">
          Rapports
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Visualisation et gestion des rapports générés
        </p>
      </div>

      {/* Filtres et recherche */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Rechercher un rapport..."
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
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="all">Tous les types</option>
            <option value="daily">Quotidien</option>
            <option value="weekly">Hebdomadaire</option>
            <option value="monthly">Mensuel</option>
            <option value="custom">Personnalisé</option>
          </select>
          <select
            className="input-field"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">Tous les statuts</option>
            <option value="generating">En génération</option>
            <option value="completed">Terminé</option>
            <option value="failed">Échoué</option>
          </select>
        </div>
      </div>

      {/* Liste des rapports */}
      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-night-blue"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredReports.map((report: Report) => (
            <div key={report.id} className="card">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <DocumentTextIcon className="h-8 w-8 text-night-blue" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-night-blue">
                      {report.title}
                    </h3>
                    <div className="flex gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${getTypeColor(report.type)}`}>
                        {report.type === 'daily' ? 'Quotidien' :
                         report.type === 'weekly' ? 'Hebdomadaire' :
                         report.type === 'monthly' ? 'Mensuel' :
                         'Personnalisé'}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(report.status)}`}>
                        {report.status === 'generating' ? 'En génération' :
                         report.status === 'completed' ? 'Terminé' :
                         'Échoué'}
                      </span>
                    </div>
                  </div>

                  {/* Période du rapport */}
                  <div className="mt-2 flex items-center gap-2 text-sm text-gray-500">
                    <CalendarIcon className="h-4 w-4" />
                    <span>
                      Du {new Date(report.period.start_date).toLocaleDateString()} au{' '}
                      {new Date(report.period.end_date).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Résumé des statistiques */}
                  <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <ChartBarIcon className="h-4 w-4" />
                        <span>Images</span>
                      </div>
                      <p className="mt-1 text-lg font-semibold text-night-blue">
                        {report.summary.total_images}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <ChartBarIcon className="h-4 w-4" />
                        <span>Détections</span>
                      </div>
                      <p className="mt-1 text-lg font-semibold text-night-blue">
                        {report.summary.total_detections}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <ChartBarIcon className="h-4 w-4" />
                        <span>Alertes</span>
                      </div>
                      <p className="mt-1 text-lg font-semibold text-night-blue">
                        {report.summary.total_alerts}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <ChartBarIcon className="h-4 w-4" />
                        <span>Investigations</span>
                      </div>
                      <p className="mt-1 text-lg font-semibold text-night-blue">
                        {report.summary.total_investigations}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-sm text-gray-500">
                      Généré le {new Date(report.created_at).toLocaleDateString()}
                    </span>
                    <div className="flex gap-2">
                      {report.status === 'completed' && report.file_url && (
                        <button className="btn-primary text-sm flex items-center gap-2">
                          <ArrowDownTrayIcon className="h-4 w-4" />
                          Télécharger
                        </button>
                      )}
                      {report.status === 'failed' && (
                        <button className="btn-secondary text-sm">
                          Réessayer
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Message si aucun rapport */}
      {!isLoading && filteredReports.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">Aucun rapport trouvé</p>
        </div>
      )}
    </div>
  );
}; 