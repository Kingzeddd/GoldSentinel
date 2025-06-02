import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  MagnifyingGlassIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { imagesAPI } from '../services/api';
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Chip,
  ImageList,
  ImageListItem,
  ImageListItemBar
} from '@mui/material';
import {
  Search,
  FilterList,
  LocationOn,
  CalendarToday,
  Satellite,
  ZoomIn,
  Download,
  Info
} from '@mui/icons-material';
import { imageService } from '../services';

interface Image {
  id: number;
  filename: string;
  url: string;
  status: 'pending' | 'analyzed' | 'error';
  created_at: string;
  detection_count: number;
  assigned_to?: number;
  investigation_report?: string;
  is_valid_image?: boolean;
  region: string;
  capture_date: string;
  satellite: string;
  resolution: string;
  metadata: Record<string, string>;
  thumbnail_url: string;
  download_url: string;
}

const ImageCard = ({ image, onViewDetails }: { image: Image; onViewDetails: (image: Image) => void }) => (
  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
    <Box
      sx={{
        position: 'relative',
        paddingTop: '75%', // 4:3 aspect ratio
        overflow: 'hidden'
      }}
    >
      <Box
        component="img"
        src={image.thumbnail_url}
        alt={image.region}
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          top: 8,
          right: 8,
          display: 'flex',
          gap: 1
        }}
      >
        <Tooltip title="Voir les détails">
          <IconButton
            size="small"
            onClick={() => onViewDetails(image)}
            sx={{ bgcolor: 'rgba(255, 255, 255, 0.8)' }}
          >
            <ZoomIn />
          </IconButton>
        </Tooltip>
        <Tooltip title="Télécharger">
          <IconButton
            size="small"
            href={image.download_url}
            download
            sx={{ bgcolor: 'rgba(255, 255, 255, 0.8)' }}
          >
            <Download />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
    <CardContent>
      <Box display="flex" alignItems="center" gap={1} mb={1}>
        <LocationOn fontSize="small" color="action" />
        <Typography variant="body2" color="text.secondary">
          {image.region}
        </Typography>
      </Box>
      <Box display="flex" alignItems="center" gap={1} mb={1}>
        <CalendarToday fontSize="small" color="action" />
        <Typography variant="body2" color="text.secondary">
          {new Date(image.capture_date).toLocaleDateString()}
        </Typography>
      </Box>
      <Box display="flex" alignItems="center" gap={1}>
        <Satellite fontSize="small" color="action" />
        <Typography variant="body2" color="text.secondary">
          {image.satellite}
        </Typography>
      </Box>
    </CardContent>
  </Card>
);

export const ImagesPage = () => {
  const { user, hasAuthority } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [regionFilter, setRegionFilter] = useState('all');
  const [selectedImage, setSelectedImage] = useState<Image | null>(null);

  const { data: images, isLoading, error } = useQuery({
    queryKey: ['images'],
    queryFn: () => imageService.getImages()
  });

  const filteredImages = images?.filter(image => {
    const matchesSearch = image.region.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRegion = regionFilter === 'all' || image.region === regionFilter;
    return matchesSearch && matchesRegion;
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
        Erreur lors du chargement des images
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 3 }}>
        Images Satellites
      </Typography>

      <Box display="flex" gap={2} mb={3}>
        <TextField
          fullWidth
          placeholder="Rechercher par région..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />
          }}
        />
        <TextField
          select
          label="Région"
          value={regionFilter}
          onChange={(e) => setRegionFilter(e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="all">Toutes les régions</MenuItem>
          <MenuItem value="Nord">Nord</MenuItem>
          <MenuItem value="Sud">Sud</MenuItem>
          <MenuItem value="Est">Est</MenuItem>
          <MenuItem value="Ouest">Ouest</MenuItem>
        </TextField>
      </Box>

      <Grid container spacing={3}>
        {filteredImages?.map((image) => (
          <Grid item xs={12} sm={6} md={4} key={image.id}>
            <ImageCard
              image={image}
              onViewDetails={setSelectedImage}
            />
          </Grid>
        ))}
      </Grid>

      <Dialog
        open={!!selectedImage}
        onClose={() => setSelectedImage(null)}
        maxWidth="lg"
        fullWidth
      >
        {selectedImage && (
          <>
            <DialogTitle>
              Détails de l'image
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12}>
                  <Box
                    component="img"
                    src={selectedImage.full_url}
                    alt={selectedImage.region}
                    sx={{
                      width: '100%',
                      height: 'auto',
                      borderRadius: 1
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Région
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedImage.region}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Date de capture
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {new Date(selectedImage.capture_date).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Satellite
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedImage.satellite}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Résolution
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedImage.resolution} m/pixel
                  </Typography>
                </Grid>
                {selectedImage.metadata && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Métadonnées
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {Object.entries(selectedImage.metadata).map(([key, value]) => (
                        <Chip
                          key={key}
                          label={`${key}: ${value}`}
                          size="small"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button
                href={selectedImage.download_url}
                download
                startIcon={<Download />}
              >
                Télécharger
              </Button>
              <Button onClick={() => setSelectedImage(null)}>
                Fermer
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}; 