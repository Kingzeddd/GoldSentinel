import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  MenuItem,
  Button,
  Alert,
  Tabs,
  Tab,
  Chip
} from '@mui/material';
import { SpectralMap } from '../components/SpectralMap';
import { SpectralCharts } from '../components/SpectralCharts';
import spectralService from '../services/spectral.service';
import { imagesAPI } from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`spectral-tabpanel-${index}`}
      aria-labelledby={`spectral-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export const SpectralAnalysisPage: React.FC = () => {
  const [selectedImageId, setSelectedImageId] = useState<number | null>(null);
  const [selectedRegionId, setSelectedRegionId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  // Récupération des images disponibles
  const { data: images, isLoading: imagesLoading } = useQuery({
    queryKey: ['images'],
    queryFn: () => imagesAPI.getAll(),
  });

  // Données spectrales pour l'image sélectionnée
  const { data: spectralMaps, isLoading: mapsLoading } = useQuery({
    queryKey: ['spectral-maps', selectedImageId],
    queryFn: () => spectralService.getSpectralMaps(selectedImageId!),
    enabled: !!selectedImageId,
  });

  const { data: spectralIndices, isLoading: indicesLoading } = useQuery({
    queryKey: ['spectral-indices', selectedImageId],
    queryFn: () => spectralService.getIndicesData(selectedImageId!),
    enabled: !!selectedImageId,
  });

  const { data: spectralTrends, isLoading: trendsLoading } = useQuery({
    queryKey: ['spectral-trends', selectedRegionId],
    queryFn: () => spectralService.getIndicesTrends(selectedRegionId!),
    enabled: !!selectedRegionId,
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleImageSelect = (imageId: number) => {
    setSelectedImageId(imageId);
    const selectedImage = images?.find(img => img.id === imageId);
    if (selectedImage) {
      setSelectedRegionId(selectedImage.region_id);
    }
  };

  const processedImages = images?.filter(img => img.processing_status === 'COMPLETED') || [];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 3 }}>
        Analyse Spectrale
      </Typography>

      {/* Sélection d'image */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Sélectionner une Image
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid sx={{ xs: 12, md: 6 }}>
              <TextField
                select
                fullWidth
                label="Image satellite"
                value={selectedImageId || ''}
                onChange={(e) => handleImageSelect(Number(e.target.value))}
                disabled={imagesLoading}
              >
                {processedImages.map((image) => (
                  <MenuItem key={image.id} value={image.id}>
                    {image.name} - {new Date(image.capture_date).toLocaleDateString()}
                    <Chip 
                      label={image.satellite} 
                      size="small" 
                      sx={{ ml: 1 }}
                    />
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid sx={{ xs: 12, md: 6 }}>
              {selectedImageId && (
                <Alert severity="info">
                  Image sélectionnée : {processedImages.find(img => img.id === selectedImageId)?.name}
                </Alert>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Contenu principal */}
      {selectedImageId && (
        <Box sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab label="Cartes Spectrales" />
              <Tab label="Graphiques & Tendances" />
              <Tab label="Données Détaillées" />
            </Tabs>
          </Box>

          <TabPanel value={activeTab} index={0}>
            <SpectralMap
              imageId={selectedImageId}
              spectralData={spectralMaps?.spectral_maps}
              loading={mapsLoading}
              error={spectralMaps ? undefined : 'Erreur chargement cartes'}
            />
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            <SpectralCharts
              currentData={spectralIndices}
              trendsData={spectralTrends?.trends}
              loading={indicesLoading || trendsLoading}
            />
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            {spectralIndices && (
              <Grid container spacing={3}>
                <Grid sx={{ xs: 12, md: 4 }}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom color="#4CAF50">
                        NDVI - Végétation
                      </Typography>
                      <Typography variant="h4" gutterBottom>
                        {spectralIndices.ndvi_mean?.toFixed(3) || 'N/A'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Moyenne: {spectralIndices.ndvi_data?.mean?.toFixed(3)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Écart-type: {spectralIndices.ndvi_data?.stddev?.toFixed(3)}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {spectralService.interpretIndex(spectralIndices.ndvi_mean || 0, 'ndvi').description}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid sx={{ xs: 12, md: 4 }}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom color="#2196F3">
                        NDWI - Eau
                      </Typography>
                      <Typography variant="h4" gutterBottom>
                        {spectralIndices.ndwi_mean?.toFixed(3) || 'N/A'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Moyenne: {spectralIndices.ndwi_data?.mean?.toFixed(3)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Écart-type: {spectralIndices.ndwi_data?.stddev?.toFixed(3)}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {spectralService.interpretIndex(spectralIndices.ndwi_mean || 0, 'ndwi').description}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid sx={{ xs: 12, md: 4 }}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom color="#FF9800">
                        NDTI - Sol
                      </Typography>
                      <Typography variant="h4" gutterBottom>
                        {spectralIndices.ndti_mean?.toFixed(3) || 'N/A'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Moyenne: {spectralIndices.ndti_data?.mean?.toFixed(3)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Écart-type: {spectralIndices.ndti_data?.stddev?.toFixed(3)}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {spectralService.interpretIndex(spectralIndices.ndti_mean || 0, 'ndti').description}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid sx={{ xs: 12 }}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Métadonnées de Traitement
                      </Typography>
                      <Typography variant="body2">
                        <strong>Statut:</strong> {spectralIndices.processing_status}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Traité le:</strong> {new Date(spectralIndices.processed_at).toLocaleString()}
                      </Typography>
                      <Typography variant="body2">
                        <strong>NDVI calculé le:</strong> {new Date(spectralIndices.ndvi_data?.computed_at).toLocaleString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}
          </TabPanel>
        </Box>
      )}

      {!selectedImageId && (
        <Alert severity="info" sx={{ mt: 3 }}>
          Sélectionnez une image pour commencer l'analyse spectrale
        </Alert>
      )}
    </Box>
  );
};
