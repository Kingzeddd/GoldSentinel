import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { MainLayout } from './layouts/MainLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ImagesPage } from './pages/ImagesPage';
import { DetectionsPage } from './pages/DetectionsPage';
import { AlertsPage } from './pages/AlertsPage';
import { InvestigationsPage } from './pages/InvestigationsPage';
import { ReportsPage } from './pages/ReportsPage';
import { RegionsPage } from './pages/RegionsPage';
import { AccountPage } from './pages/AccountPage';
import { SpectralAnalysisPage } from './pages/SpectralAnalysisPage';

// Création du client React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <DashboardPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/images"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <ImagesPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/detections"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <DetectionsPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/alerts"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <AlertsPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/investigations"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <InvestigationsPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <ReportsPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/stats"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    {/* TODO: Ajouter la page des statistiques */}
                    <div>Statistiques</div>
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/regions"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <RegionsPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/account"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <AccountPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/spectral"
              element={
                <ProtectedRoute>
                  <MainLayout>
                    <SpectralAnalysisPage />
                  </MainLayout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
