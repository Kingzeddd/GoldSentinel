import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  UserCircleIcon,
  EnvelopeIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { accountAPI } from '../services/api';

interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name: string;
  job_title: string;
  institution: string;
  authorized_region: string;
  primary_authority: string;
  created_at: string;
  last_login: string;
}

export const AccountPage: React.FC = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    job_title: '',
    institution: '',
  });

  const queryClient = useQueryClient();

  // Requête pour le profil utilisateur
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => accountAPI.getProfile(),
    onSuccess: (data) => { // Assuming data is UserProfile directly
      if (data) { // Check if data is not undefined
        setFormData({
          full_name: data.full_name || '',
          job_title: data.job_title || '',
          institution: data.institution || '',
        });
      }
    },
  });

  // Mutation pour mettre à jour le profil
  const updateProfile = useMutation({
    mutationFn: (data: typeof formData) => accountAPI.updateProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      setIsEditing(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfile.mutate(formData);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-night-blue"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-heading font-semibold text-night-blue">
          Mon Profil
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Gérez vos informations personnelles et vos paramètres
        </p>
      </div>

      <div className="card">
        <div className="flex items-start gap-6">
          <div className="flex-shrink-0">
            <UserCircleIcon className="h-24 w-24 text-gray-400" />
          </div>
          <div className="flex-1">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-night-blue mb-4">
                  Informations personnelles
                </h3>
                {isEditing ? (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nom complet
                      </label>
                      <input
                        type="text"
                        className="input-field"
                        value={formData.full_name}
                        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Poste
                      </label>
                      <input
                        type="text"
                        className="input-field"
                        value={formData.job_title}
                        onChange={(e) => setFormData({ ...formData, job_title: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Institution
                      </label>
                      <input
                        type="text"
                        className="input-field"
                        value={formData.institution}
                        onChange={(e) => setFormData({ ...formData, institution: e.target.value })}
                      />
                    </div>
                    <div className="flex gap-4">
                      <button
                        type="button"
                        onClick={() => setIsEditing(false)}
                        className="btn-secondary"
                      >
                        Annuler
                      </button>
                      <button type="submit" className="btn-primary">
                        Enregistrer
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nom complet
                      </label>
                      <p className="text-gray-900">{profile?.full_name}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Poste
                      </label>
                      <p className="text-gray-900">{profile?.job_title}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Institution
                      </label>
                      <p className="text-gray-900">{profile?.institution}</p>
                    </div>
                    <button
                      onClick={() => setIsEditing(true)}
                      className="btn-primary"
                    >
                      Modifier
                    </button>
                  </div>
                )}
              </div>

              <div>
                <h3 className="text-lg font-medium text-night-blue mb-4">
                  Informations système
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nom d'utilisateur
                    </label>
                    <p className="text-gray-900">{profile?.username}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <p className="text-gray-900">{profile?.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Rôle
                    </label>
                    <p className="text-gray-900">{profile?.primary_authority}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Région assignée
                    </label>
                    <p className="text-gray-900">{profile?.authorized_region}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Dernière connexion
                    </label>
                    <p className="text-gray-900">
                      {profile?.last_login ? new Date(profile.last_login).toLocaleString() : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 