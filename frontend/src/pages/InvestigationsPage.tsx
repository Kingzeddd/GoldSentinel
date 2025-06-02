import { useState } from 'react';
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
  MenuItem,
  Avatar,
  AvatarGroup,
  Snackbar,
  TablePagination,
  Grid,
  Fade
} from '@mui/material';
import {
  Assignment,
  CheckCircle,
  Cancel,
  Visibility,
  Edit,
  Person,
  LocationOn,
  CalendarToday,
  FilterList
} from '@mui/icons-material';
import { investigationService } from '../services';

const InvestigationStatusChip = ({ status }: { status: string }) => {
  const getStatusColor = () => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'warning';
      case 'in_progress':
        return 'info';
      case 'completed':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = () => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'En attente';
      case 'in_progress':
        return 'En cours';
      case 'completed':
        return 'Terminée';
      case 'cancelled':
        return 'Annulée';
      default:
        return status;
    }
  };

  return (
    <Chip
      label={getStatusLabel()}
      color={getStatusColor()}
      size="small"
    />
  );
};

export const InvestigationsPage = () => {
  const [selectedInvestigation, setSelectedInvestigation] = useState<any>(null);
  const [updateDialogOpen, setUpdateDialogOpen] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [newComment, setNewComment] = useState('');
  
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: null,
    agent: 'all',
    region: 'all'
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  const queryClient = useQueryClient();

  const { data: investigations, isLoading, error } = useQuery({
    queryKey: ['investigations'],
    queryFn: () => investigationService.getInvestigations()
  });

  const updateInvestigationMutation = useMutation({
    mutationFn: (data: { id: string; status: string; comment: string }) =>
      investigationService.updateInvestigation(data.id, data.status, data.comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investigations'] });
      setUpdateDialogOpen(false);
      setSelectedInvestigation(null);
      showMessage('Investigation mise à jour avec succès', 'success');
    },
    onError: (error: any) => {
      showMessage(error.message || 'Erreur lors de la mise à jour', 'error');
    }
  });

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const showMessage = (message: string, severity: 'success' | 'error') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleUpdateInvestigation = () => {
    if (selectedInvestigation && newStatus) {
      updateInvestigationMutation.mutate({
        id: selectedInvestigation.id,
        status: newStatus,
        comment: newComment
      });
    }
  };

  const filteredInvestigations = investigations?.filter(investigation => {
    if (filters.status !== 'all' && investigation.status !== filters.status) return false;
    if (filters.agent !== 'all' && !investigation.agents.some((a: any) => a.id === filters.agent)) return false;
    if (filters.region !== 'all' && investigation.region !== filters.region) return false;
    return true;
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
        Erreur lors du chargement des investigations
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 3 }}>
        Investigations
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
              <TextField
                select
                fullWidth
                label="Statut"
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              >
                <MenuItem value="all">Tous les statuts</MenuItem>
                <MenuItem value="pending">En attente</MenuItem>
                <MenuItem value="in_progress">En cours</MenuItem>
                <MenuItem value="completed">Terminée</MenuItem>
                <MenuItem value="cancelled">Annulée</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                select
                fullWidth
                label="Agent"
                value={filters.agent}
                onChange={(e) => setFilters({ ...filters, agent: e.target.value })}
              >
                <MenuItem value="all">Tous les agents</MenuItem>
                {investigations?.flatMap((i: any) => i.agents)
                  .filter((a: any, index: number, self: any[]) => 
                    index === self.findIndex((t: any) => t.id === a.id)
                  )
                  .map((agent: any) => (
                    <MenuItem key={agent.id} value={agent.id}>
                      {agent.name}
                    </MenuItem>
                  ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                select
                fullWidth
                label="Région"
                value={filters.region}
                onChange={(e) => setFilters({ ...filters, region: e.target.value })}
              >
                <MenuItem value="all">Toutes les régions</MenuItem>
                {investigations?.map((i: any) => i.region)
                  .filter((r: string, index: number, self: string[]) => 
                    index === self.indexOf(r)
                  )
                  .map((region: string) => (
                    <MenuItem key={region} value={region}>
                      {region}
                    </MenuItem>
                  ))}
              </TextField>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Région</TableCell>
                  <TableCell>Statut</TableCell>
                  <TableCell>Agents</TableCell>
                  <TableCell>Date de Création</TableCell>
                  <TableCell>Dernière Mise à Jour</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredInvestigations
                  ?.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((investigation) => (
                    <Fade in={true} key={investigation.id}>
                      <TableRow>
                        <TableCell>{investigation.id}</TableCell>
                        <TableCell>{investigation.type}</TableCell>
                        <TableCell>{investigation.region}</TableCell>
                        <TableCell>
                          <InvestigationStatusChip status={investigation.status} />
                        </TableCell>
                        <TableCell>
                          <AvatarGroup max={3}>
                            {investigation.agents.map((agent: any) => (
                              <Tooltip key={agent.id} title={agent.name}>
                                <Avatar sx={{ width: 32, height: 32 }}>
                                  {agent.name.charAt(0)}
                                </Avatar>
                              </Tooltip>
                            ))}
                          </AvatarGroup>
                        </TableCell>
                        <TableCell>
                          {new Date(investigation.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          {new Date(investigation.updated_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={1}>
                            <Tooltip title="Voir les détails">
                              <IconButton
                                size="small"
                                onClick={() => setSelectedInvestigation(investigation)}
                              >
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Mettre à jour le statut">
                              <IconButton
                                size="small"
                                onClick={() => {
                                  setSelectedInvestigation(investigation);
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
                    </Fade>
                  ))}
              </TableBody>
            </Table>
            <TablePagination
              rowsPerPageOptions={[10, 20, 50]}
              component="div"
              count={filteredInvestigations?.length || 0}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
              labelRowsPerPage="Lignes par page"
            />
          </TableContainer>
        </CardContent>
      </Card>

      <Dialog
        open={updateDialogOpen}
        onClose={() => setUpdateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Mettre à jour l'investigation</DialogTitle>
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
              <MenuItem value="pending">En attente</MenuItem>
              <MenuItem value="in_progress">En cours</MenuItem>
              <MenuItem value="completed">Terminée</MenuItem>
              <MenuItem value="cancelled">Annulée</MenuItem>
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
            onClick={handleUpdateInvestigation}
            variant="contained"
            disabled={!newStatus}
          >
            Mettre à jour
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      <Dialog
        open={!!selectedInvestigation}
        onClose={() => setSelectedInvestigation(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedInvestigation && (
          <>
            <DialogTitle>
              Détails de l'investigation
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Type
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedInvestigation.type}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Statut
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    <InvestigationStatusChip status={selectedInvestigation.status} />
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Région
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedInvestigation.region}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Date de création
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {new Date(selectedInvestigation.created_at).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Agents assignés
                  </Typography>
                  <Box display="flex" gap={1} mt={1}>
                    {selectedInvestigation.agents.map((agent: any) => (
                      <Chip
                        key={agent.id}
                        avatar={<Avatar>{agent.name.charAt(0)}</Avatar>}
                        label={agent.name}
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Grid>
                {selectedInvestigation.comments && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Commentaires
                    </Typography>
                    <Typography variant="body1" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
                      {selectedInvestigation.comments}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedInvestigation(null)}>
                Fermer
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}; 