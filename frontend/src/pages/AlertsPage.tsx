import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Visibility,
  Edit,
  Warning,
  Error,
  Info
} from '@mui/icons-material';
import { alertService } from '../services';

const AlertStatusChip = ({ status }: { status: string }) => {
  const getStatusColor = () => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'error';
      case 'resolved':
        return 'success';
      case 'investigating':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = () => {
    switch (status.toLowerCase()) {
      case 'active':
        return <Error fontSize="small" />;
      case 'resolved':
        return <CheckCircle fontSize="small" />;
      case 'investigating':
        return <Warning fontSize="small" />;
      default:
        return <Info fontSize="small" />;
    }
  };

  return (
    <Chip
      icon={getStatusIcon()}
      label={status}
      color={getStatusColor()}
      size="small"
    />
  );
};

const AlertLevelChip = ({ level }: { level: string }) => {
  const getLevelColor = () => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Chip
      label={level}
      color={getLevelColor()}
      size="small"
    />
  );
};

export const AlertsPage = () => {
  const [selectedAlert, setSelectedAlert] = useState<any>(null);
  const [updateDialogOpen, setUpdateDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [newComment, setNewComment] = useState('');
  const queryClient = useQueryClient();

  const { data: alerts, isLoading, error } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertService.getActiveAlerts()
  });

  const updateAlertMutation = useMutation({
    mutationFn: (data: { id: string; status: string; comment: string }) =>
      alertService.updateAlertStatus(data.id, data.status, data.comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      setUpdateDialogOpen(false);
      setSelectedAlert(null);
    }
  });

  const handleUpdateAlert = () => {
    if (selectedAlert && newStatus) {
      updateAlertMutation.mutate({
        id: selectedAlert.id,
        status: newStatus,
        comment: newComment
      });
    }
  };

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
        Erreur lors du chargement des alertes
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 3 }}>
        Gestion des Alertes
      </Typography>

      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Niveau</TableCell>
                  <TableCell>Statut</TableCell>
                  <TableCell>Date de Création</TableCell>
                  <TableCell>Dernière Mise à Jour</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {alerts?.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell>{alert.id}</TableCell>
                    <TableCell>{alert.type}</TableCell>
                    <TableCell>
                      <AlertLevelChip level={alert.level} />
                    </TableCell>
                    <TableCell>
                      <AlertStatusChip status={alert.status} />
                    </TableCell>
                    <TableCell>
                      {new Date(alert.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      {new Date(alert.updated_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Tooltip title="Voir les détails">
                          <IconButton
                            size="small"
                            onClick={() => setSelectedAlert(alert)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Mettre à jour le statut">
                          <IconButton
                            size="small"
                            onClick={() => {
                              setSelectedAlert(alert);
                              setNewStatus('');
                              setNewComment('');
                              setUpdateDialogOpen(true);
                            }}
                          >
                            <Edit />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <Dialog
        open={updateDialogOpen}
        onClose={() => setUpdateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Mettre à jour le statut de l'alerte</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              select
              fullWidth
              label="Nouveau statut"
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              sx={{ mb: 2 }}
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="investigating">En investigation</MenuItem>
              <MenuItem value="resolved">Résolue</MenuItem>
            </TextField>
            <TextField
              fullWidth
              label="Commentaire"
              multiline
              rows={4}
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpdateDialogOpen(false)}>Annuler</Button>
          <Button
            onClick={handleUpdateAlert}
            variant="contained"
            disabled={!newStatus}
          >
            Mettre à jour
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 