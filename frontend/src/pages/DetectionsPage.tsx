import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  MagnifyingGlassIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { detectionsAPI } from '../services/api';
import { SpectralMap } from '../components/SpectralMap';
import { SpectralCharts } from '../components/SpectralCharts';
import spectralService from '../services/spectral.service';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  MenuItem,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Rating
} from '@mui/material';
import {
  Search,
  FilterList,
  LocationOn,
  CalendarToday,
  CheckCircle,
  Cancel,
  Visibility
} from '@mui/icons-material';
import { detectionService } from '../services';

interface Detection {
  id: number;
  image_url: string;
  confidence: number;
  created_at: string;
  status: 'pending' | 'validated' | 'rejected';
  location: string;
  assigned_to?: number;
  investigation_report?: string;
  is_true_detection?: boolean;
}

const DetectionCard = ({ detection, onViewDetails }: { detection: any; onViewDetails: (detection: any) => void }) => (
  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
        <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
          {detection.type}
        </Typography>
        <Chip
          label={`${(detection.confidence_score * 100).toFixed(1)}%`}
          color={detection.confidence_score > 0.8 ? 'success' : detection.confidence_score > 0.5 ? 'warning' : 'error'}
          size="small"
        />
      </Box>

      <Box display="flex" alignItems="center" gap={1} mb={1}>
        <LocationOn fontSize="small" color="action" />
        <Typography variant="body2" color="text.secondary">
          {detection.region}
        </Typography>
      </Box>

      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <CalendarToday fontSize="small" color="action" />
        <Typography variant="body2" color="text.secondary">
          {new Date(detection.detection_date).toLocaleDateString()}
        </Typography>
      </Box>

      <Typography variant="body2" color="text.secondary" mb={2}>
        Surface: {detection.area_hectares.toFixed(2)} hectares
      </Typography>

      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Validation
          </Typography>
          <Rating
            value={detection.validation_status === 'validated' ? 1 : detection.validation_status === 'rejected' ? 0 : 0.5}
            readOnly
            precision={0.5}
            icon={<CheckCircle fontSize="small" />}
            emptyIcon={<Cancel fontSize="small" />}
          />
        </Box>
        <Tooltip title="Voir les détails">
          <IconButton
            size="small"
            onClick={() => onViewDetails(detection)}
          >
            <Visibility />
          </IconButton>
        </Tooltip>
      </Box>
    </CardContent>
  </Card>
);

export const DetectionsPage = () => {
  const { user, hasAuthority } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [selectedDetection, setSelectedDetection] = useState<any>(null);
  const [showSpectralData, setShowSpectralData] = useState(false);

  const queryClient = useQueryClient();

  const { data: detections, isLoading, error } = useQuery({
    queryKey: ['detections'],
    queryFn: () => detectionService.getDetections()
  });

  // Requêtes pour les données spectrales
  const { data: spectralMaps, isLoading: spectralLoading } = useQuery({
    queryKey: ['spectral-maps', selectedDetection?.image_id],
    queryFn: () => spectralService.getSpectralMaps(selectedDetection.image_id),
    enabled: !!selectedDetection?.image_id && showSpectralData,
  });

  const { data: spectralIndices } = useQuery({
    queryKey: ['spectral-indices', selectedDetection?.image_id],
    queryFn: () => spectralService.getIndicesData(selectedDetection.image_id),
    enabled: !!selectedDetection?.image_id,
  });

  const { data: spectralTrends } = useQuery({
    queryKey: ['spectral-trends', selectedDetection?.region_id],
    queryFn: () => spectralService.getIndicesTrends(selectedDetection.region_id),
    enabled: !!selectedDetection?.region_id && showSpectralData,
  });

  const filteredDetections = detections?.filter(detection => {
    const matchesSearch = detection.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         detection.region.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === 'all' || detection.type === typeFilter;
    return matchesSearch && matchesType;
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
        Erreur lors du chargement des détections
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 3 }}>
          Détections
      </Typography>

      <Box display="flex" gap={2} mb={3}>
        <TextField
          fullWidth
          placeholder="Rechercher par type ou région..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />
          }}
        />
        <TextField
          select
          label="Type"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="all">Tous les types</MenuItem>
          <MenuItem value="mining">Exploitation minière</MenuItem>
          <MenuItem value="deforestation">Déforestation</MenuItem>
          <MenuItem value="construction">Construction</MenuItem>
        </TextField>
      </Box>

      <Grid container spacing={3}>
        {filteredDetections?.map((detection) => (
          <Grid item xs={12} sm={6} md={4} key={detection.id}>
            <DetectionCard
              detection={detection}
              onViewDetails={setSelectedDetection}
            />
          </Grid>
        ))}
      </Grid>

      <Dialog
        open={!!selectedDetection}
        onClose={() => setSelectedDetection(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedDetection && (
          <>
            <DialogTitle>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                Détails de la détection
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setShowSpectralData(!showSpectralData)}
                >
                  {showSpectralData ? 'Masquer' : 'Afficher'} Données Spectrales
                </Button>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Type
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedDetection.type}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Score de confiance
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {(selectedDetection.confidence_score * 100).toFixed(1)}%
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Région
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedDetection.region}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Date de détection
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {new Date(selectedDetection.detection_date).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Surface
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedDetection.area_hectares.toFixed(2)} hectares
                  </Typography>
                </Grid>
                {selectedDetection.image_url && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Image satellite
                    </Typography>
                    <Box
                      component="img"
                      src={selectedDetection.image_url}
                      alt="Détection"
                      sx={{
                        width: '100%',
                        height: 'auto',
                        borderRadius: 1
                      }}
                    />
                  </Grid>
                )}

                {/* Données spectrales */}
                {showSpectralData && (
                  <>
                    <Grid item xs={12}>
                      <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                        Analyse Spectrale
                      </Typography>
                    </Grid>

                    {/* Cartes spectrales */}
                    <Grid item xs={12}>
                      <SpectralMap
                        imageId={selectedDetection.image_id}
                        spectralData={spectralMaps?.spectral_maps}
                        loading={spectralLoading}
                        error={spectralMaps ? undefined : 'Erreur chargement cartes'}
                      />
                    </Grid>

                    {/* Graphiques et données */}
                    <Grid item xs={12}>
                      <SpectralCharts
                        currentData={spectralIndices}
                        trendsData={spectralTrends?.trends}
                        loading={spectralLoading}
                      />
                    </Grid>

                    {/* Indices détaillés */}
                    {spectralIndices && (
                      <Grid item xs={12}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Valeurs des Indices
                            </Typography>
                            <Grid container spacing={2}>
                              <Grid item xs={4}>
                                <Typography variant="body2" color="text.secondary">
                                  NDVI (Végétation)
                                </Typography>
                                <Typography variant="h6" color="#4CAF50">
                                  {spectralIndices.ndvi_mean?.toFixed(3) || 'N/A'}
                                </Typography>
                                <Typography variant="caption">
                                  {spectralService.interpretIndex(spectralIndices.ndvi_mean || 0, 'ndvi').description}
                                </Typography>
                              </Grid>
                              <Grid item xs={4}>
                                <Typography variant="body2" color="text.secondary">
                                  NDWI (Eau)
                                </Typography>
                                <Typography variant="h6" color="#2196F3">
                                  {spectralIndices.ndwi_mean?.toFixed(3) || 'N/A'}
                                </Typography>
                                <Typography variant="caption">
                                  {spectralService.interpretIndex(spectralIndices.ndwi_mean || 0, 'ndwi').description}
                                </Typography>
                              </Grid>
                              <Grid item xs={4}>
                                <Typography variant="body2" color="text.secondary">
                                  NDTI (Sol)
                                </Typography>
                                <Typography variant="h6" color="#FF9800">
                                  {spectralIndices.ndti_mean?.toFixed(3) || 'N/A'}
                                </Typography>
                                <Typography variant="caption">
                                  {spectralService.interpretIndex(spectralIndices.ndti_mean || 0, 'ndti').description}
                                </Typography>
                              </Grid>
                            </Grid>
                          </CardContent>
                        </Card>
                      </Grid>
                    )}
                  </>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedDetection(null)}>
                Fermer
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};