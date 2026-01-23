import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores';
import { LoadingSpinner } from '@/components/ui';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireOnboarding?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireOnboarding = true 
}) => {
  const { isAuthenticated, isLoading, profile } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if user has completed onboarding (has profile with required fields)
  if (requireOnboarding && profile !== undefined) {
    const hasCompletedOnboarding = profile && 
      profile.first_name && 
      profile.height_cm && 
      profile.current_weight_kg;
    
    if (!hasCompletedOnboarding && location.pathname !== '/onboarding') {
      return <Navigate to="/onboarding" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
