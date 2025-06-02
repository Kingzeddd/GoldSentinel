import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';
import { Box, Card, CardContent, Typography, Grid, Chip } from '@mui/material';

interface SpectralData {
  ndvi_data?: {
    mean: number;
    stddev: number;
    computed_at: string;
  };
  ndwi_data?: {
    mean: number;
    stddev: number;
    computed_at: string;
  };
  ndti_data?: {
    mean: number;
    stddev: number;
    computed_at: string;
  };
}

interface TrendData {
  date: string;
  ndvi_mean: number;
  ndwi_mean: number;
  ndti_mean: number;
  image_id: number;
}

interface SpectralChartsProps {
  currentData?: SpectralData;
  trendsData?: TrendData[];
  loading?: boolean;
}

const getIndexColor = (index: string) => {
  switch (index) {
    case 'ndvi': return '#4CAF50';
    case 'ndwi': return '#2196F3';
    case 'ndti': return '#FF9800';
    default: return '#757575';
  }
};

const getIndexStatus = (value: number, index: string) => {
  if (index === 'ndvi') {
    if (value > 0.6) return { label: 'Végétation dense', color: 'success' };
    if (value > 0.3) return { label: 'Végétation modérée', color: 'warning' };
    return { label: 'Végétation faible', color: 'error' };
  }
  if (index === 'ndwi') {
    if (value > 0.3) return { label: 'Eau présente', color: 'info' };
    if (value > 0) return { label: 'Humidité', color: 'warning' };
    return { label: 'Sec', color: 'default' };
  }
  if (index === 'ndti') {
    if (value > 0.2) return { label: 'Sol perturbé', color: 'error' };
    if (value > 0) return { label: 'Sol modifié', color: 'warning' };
    return { label: 'Sol naturel', color: 'success' };
  }
  return { label: 'Normal', color: 'default' };
};

export const SpectralCharts: React.FC<SpectralChartsProps> = ({
  currentData,
  trendsData,
  loading = false
}) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <Typography>Chargement des données spectrales...</Typography>
      </Box>
    );
  }

  // Préparation des données pour le graphique en barres
  const barData = currentData ? [
    {
      name: 'NDVI',
      value: currentData.ndvi_data?.mean || 0,
      stddev: currentData.ndvi_data?.stddev || 0
    },
    {
      name: 'NDWI',
      value: currentData.ndwi_data?.mean || 0,
      stddev: currentData.ndwi_data?.stddev || 0
    },
    {
      name: 'NDTI',
      value: currentData.ndti_data?.mean || 0,
      stddev: currentData.ndti_data?.stddev || 0
    }
  ] : [];

  // Formatage des données de tendance
  const formattedTrends = trendsData?.map(item => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('fr-FR', {
      month: 'short',
      day: 'numeric'
    })
  })) || [];

  return (
    <Grid container spacing={3}>
      {/* Valeurs actuelles */}
      {currentData && (
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Indices Spectraux Actuels
              </Typography>
              
              <Box mb={3}>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={barData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis domain={[-1, 1]} />
                    <Tooltip 
                      formatter={(value: number, name: string) => [
                        value.toFixed(3),
                        name === 'value' ? 'Moyenne' : 'Écart-type'
                      ]}
                    />
                    <Bar dataKey="value" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>

              <Grid container spacing={2}>
                {['ndvi', 'ndwi', 'ndti'].map((index) => {
                  const data = currentData[`${index}_data` as keyof SpectralData];
                  const mean = data?.mean || 0;
                  const status = getIndexStatus(mean, index);
                  
                  return (
                    <Grid item xs={12} key={index}>
                      <Box display="flex" justifyContent="space-between" alignItems="center" p={1}>
                        <Typography variant="body2" sx={{ color: getIndexColor(index), fontWeight: 'bold' }}>
                          {index.toUpperCase()}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2">
                            {mean.toFixed(3)}
                          </Typography>
                          <Chip 
                            label={status.label} 
                            size="small" 
                            color={status.color as any}
                          />
                        </Box>
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      )}

      {/* Évolution temporelle */}
      {trendsData && trendsData.length > 0 && (
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Évolution Temporelle (30 jours)
              </Typography>
              
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={formattedTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[-1, 1]} />
                  <Tooltip 
                    formatter={(value: number) => [value.toFixed(3), '']}
                    labelFormatter={(label) => `Date: ${label}`}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="ndvi_mean" 
                    stroke={getIndexColor('ndvi')} 
                    strokeWidth={2}
                    name="NDVI"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="ndwi_mean" 
                    stroke={getIndexColor('ndwi')} 
                    strokeWidth={2}
                    name="NDWI"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="ndti_mean" 
                    stroke={getIndexColor('ndti')} 
                    strokeWidth={2}
                    name="NDTI"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );
};
