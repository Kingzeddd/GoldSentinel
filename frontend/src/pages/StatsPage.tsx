import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Box, 
  CircularProgress,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import {
  TrendingUp,
  Warning,
  Search,
  Assessment,
  AttachMoney,
  Refresh
} from '@mui/icons-material';
import { statsService } from '../services';

const StatCard = ({ title, value, icon, color }: { title: string; value: string | number; icon: React.ReactNode; color: string }) => (
  <Card sx={{ height: '100%', bgcolor: 'background.paper' }}>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <Box
          sx={{
            backgroundColor: `${color}15`,
            borderRadius: '12px',
            p: 1,
            mr: 2
          }}
        >
          {icon}
        </Box>
        <Typography variant="h6" color="text.secondary">
          {title}
        </Typography>
      </Box>
      <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
        {value}
      </Typography>
    </CardContent>
  </Card>
);

export const StatsPage = () => {
  const { data: dashboardStats, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => statsService.getDashboardStats()
  });

  const { data: financialImpact } = useQuery({
    queryKey: ['financialImpact'],
    queryFn: () => statsService.getFinancialImpact()
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        Erreur lors du chargement des statistiques
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Tableau de Bord
        </Typography>
        <Tooltip title="Actualiser">
          <IconButton onClick={() => refetch()} color="primary">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3} mb={4}>
        <Grid sx={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Détections Totales"
            value={dashboardStats?.total_detections || 0}
            icon={<Search sx={{ color: '#2196f3' }} />}
            color="#2196f3"
          />
        </Grid>
        <Grid sx={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Alertes Actives"
            value={dashboardStats?.active_alerts || 0}
            icon={<Warning sx={{ color: '#f44336' }} />}
            color="#f44336"
          />
        </Grid>
        <Grid sx={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Investigations en Attente"
            value={dashboardStats?.pending_investigations || 0}
            icon={<Assessment sx={{ color: '#ff9800' }} />}
            color="#ff9800"
          />
        </Grid>
        <Grid sx={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            title="Risque Financier"
            value={`${(dashboardStats?.total_financial_risk || 0).toLocaleString()} FCFA`}
            icon={<AttachMoney sx={{ color: '#4caf50' }} />}
            color="#4caf50"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid sx={{ xs: 12, md: 8 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Tendances des Détections
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={dashboardStats?.detections_trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#2196f3"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid sx={{ xs: 12, md: 4 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Alertes par Niveau
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={Object.entries(dashboardStats?.alerts_by_level || {}).map(([level, count]) => ({
                    level,
                    count
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="level" />
                    <YAxis />
                    <RechartsTooltip />
                    <Bar dataKey="count" fill="#f44336" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid sx={{ xs: 12 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Impact Financier par Niveau de Risque
              </Typography>
              <Box height={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={financialImpact?.breakdown_by_risk_level}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="risk_level" />
                    <YAxis />
                    <RechartsTooltip />
                    <Bar dataKey="total_amount" fill="#4caf50" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}; 