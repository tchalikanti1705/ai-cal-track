import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from '@/stores';
import { Layout, ProtectedRoute } from '@/components/layout';
import {
  LoginPage,
  RegisterPage,
  DashboardPage,
  NutritionPage,
  WaterPage,
  ExercisePage,
  WalkingPage,
  FoodScanPage,
  InsightsPage,
  OnboardingPage,
} from '@/pages';

const App: React.FC = () => {
  const { loadUser, isAuthenticated, loadProfile } = useAuthStore();

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (isAuthenticated) {
      loadProfile();
    }
  }, [isAuthenticated, loadProfile]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route 
          path="/login" 
          element={isAuthenticated ? <Navigate to="/dashboard" /> : <LoginPage />} 
        />
        <Route 
          path="/register" 
          element={isAuthenticated ? <Navigate to="/onboarding" /> : <RegisterPage />} 
        />

        {/* Onboarding - protected but doesn't require onboarding completion */}
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute requireOnboarding={false}>
              <OnboardingPage />
            </ProtectedRoute>
          }
        />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/nutrition"
          element={
            <ProtectedRoute>
              <Layout>
                <NutritionPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/water"
          element={
            <ProtectedRoute>
              <Layout>
                <WaterPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/exercise"
          element={
            <ProtectedRoute>
              <Layout>
                <ExercisePage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/walking"
          element={
            <ProtectedRoute>
              <Layout>
                <WalkingPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/scan"
          element={
            <ProtectedRoute>
              <Layout>
                <FoodScanPage />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/insights"
          element={
            <ProtectedRoute>
              <Layout>
                <InsightsPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Redirect root to dashboard or login */}
        <Route 
          path="/" 
          element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} 
        />

        {/* 404 */}
        <Route 
          path="*" 
          element={<Navigate to="/" />} 
        />
      </Routes>

      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#1e293b',
            color: '#fff',
            borderRadius: '0.75rem',
          },
          success: {
            iconTheme: {
              primary: '#22c55e',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </BrowserRouter>
  );
};

export default App;
