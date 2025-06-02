import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Rectangle, useMap } from 'react-leaflet';
import { LatLngBounds } from 'leaflet';
import { Box, Card, CardContent, Typography, Tabs, Tab, CircularProgress, Alert } from '@mui/material';
import 'leaflet/dist/leaflet.css';

interface SpectralMapProps {
  imageId: number;
  spectralData?: {
    ndvi_map_url: string;
    ndwi_map_url: string;
    ndti_map_url: string;
    bounds: {
      north: number;
      south: number;
      east: number;
      west: number;
    };
  };
  loading?: boolean;
  error?: string;
}

interface SpectralLayerProps {
  url: string;
  bounds: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
}

const SpectralLayer: React.FC<SpectralLayerProps> = ({ url, bounds }) => {
  const map = useMap();

  useEffect(() => {
    if (url && bounds) {
      const leafletBounds = new LatLngBounds(
        [bounds.south, bounds.west],
        [bounds.north, bounds.east]
      );

      // Création de la couche de tuiles personnalisée
      const spectralLayer = new (window as any).L.TileLayer(url, {
        opacity: 0.7,
        bounds: leafletBounds
      });

      map.addLayer(spectralLayer);
      map.fitBounds(leafletBounds);

      return () => {
        map.removeLayer(spectralLayer);
      };
    }
  }, [map, url, bounds]);

  return null;
};

export const SpectralMap: React.FC<SpectralMapProps> = ({
  imageId,
  spectralData,
  loading = false,
  error
}) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
            <CircularProgress />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Chargement des cartes spectrales...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!spectralData) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">Aucune donnée spectrale disponible</Alert>
        </CardContent>
      </Card>
    );
  }

  const tabs = [
    { label: 'NDVI (Végétation)', url: spectralData.ndvi_map_url, color: '#4CAF50' },
    { label: 'NDWI (Eau)', url: spectralData.ndwi_map_url, color: '#2196F3' },
    { label: 'NDTI (Sol)', url: spectralData.ndti_map_url, color: '#FF9800' }
  ];

  const center: [number, number] = [
    (spectralData.bounds.north + spectralData.bounds.south) / 2,
    (spectralData.bounds.east + spectralData.bounds.west) / 2
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Cartes d'Indices Spectraux
        </Typography>
        
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              label={tab.label}
              sx={{
                color: tab.color,
                '&.Mui-selected': {
                  color: tab.color,
                  fontWeight: 'bold'
                }
              }}
            />
          ))}
        </Tabs>

        <Box height={400} sx={{ border: '1px solid #ddd', borderRadius: 1 }}>
          <MapContainer
            center={center}
            zoom={12}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            
            {tabs[activeTab] && (
              <SpectralLayer
                url={tabs[activeTab].url}
                bounds={spectralData.bounds}
              />
            )}

            <Rectangle
              bounds={[
                [spectralData.bounds.south, spectralData.bounds.west],
                [spectralData.bounds.north, spectralData.bounds.east]
              ]}
              pathOptions={{ color: tabs[activeTab].color, weight: 2, fillOpacity: 0 }}
            />
          </MapContainer>
        </Box>

        <Box mt={2}>
          <Typography variant="body2" color="text.secondary">
            <strong>Légende :</strong>
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • NDVI : Rouge = Pas de végétation, Vert = Végétation dense
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • NDWI : Blanc = Sec, Bleu = Présence d'eau
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • NDTI : Bleu = Sol naturel, Rouge = Sol perturbé
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
