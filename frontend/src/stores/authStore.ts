import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, UserProfile, UserGoals, AuthTokens } from '@/types';
import { authService, userService } from '@/services';

interface AuthState {
  user: User | null;
  profile: UserProfile | null;
  goals: UserGoals | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, firstName?: string, lastName?: string) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  loadProfile: () => Promise<void>;
  loadGoals: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<void>;
  updateGoals: (data: Partial<UserGoals>) => Promise<void>;
  clearError: () => void;
  setTokens: (tokens: AuthTokens) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      profile: null,
      goals: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await authService.login({ email, password });
          authService.setTokens(tokens);
          
          const user = await authService.getCurrentUser();
          
          set({ 
            user, 
            isAuthenticated: true, 
            isLoading: false 
          });

          // Load profile and goals in background
          get().loadProfile();
          get().loadGoals();
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Login failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      register: async (email: string, password: string, firstName?: string, lastName?: string) => {
        set({ isLoading: true, error: null });
        try {
          const tokens = await authService.register({ 
            email, 
            password, 
            first_name: firstName,
            last_name: lastName 
          });
          authService.setTokens(tokens);
          
          const user = await authService.getCurrentUser();
          
          set({ 
            user, 
            isAuthenticated: true, 
            isLoading: false 
          });
        } catch (error: unknown) {
          const message = error instanceof Error ? error.message : 'Registration failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          await authService.logout();
        } finally {
          set({ 
            user: null, 
            profile: null, 
            goals: null, 
            isAuthenticated: false 
          });
        }
      },

      loadUser: async () => {
        if (!authService.isAuthenticated()) {
          set({ isAuthenticated: false });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await authService.getCurrentUser();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          set({ isAuthenticated: false, isLoading: false });
          authService.clearTokens();
        }
      },

      loadProfile: async () => {
        try {
          const profile = await userService.getProfile();
          set({ profile });
        } catch (error) {
          console.error('Failed to load profile:', error);
        }
      },

      loadGoals: async () => {
        try {
          const goals = await userService.getGoals();
          set({ goals });
        } catch (error) {
          console.error('Failed to load goals:', error);
        }
      },

      updateProfile: async (data: Partial<UserProfile>) => {
        try {
          const profile = await userService.updateProfile(data as Parameters<typeof userService.updateProfile>[0]);
          set({ profile });
        } catch (error) {
          console.error('Failed to update profile:', error);
          throw error;
        }
      },

      updateGoals: async (data: Partial<UserGoals>) => {
        try {
          const goals = await userService.updateGoals(data as Parameters<typeof userService.updateGoals>[0]);
          set({ goals });
        } catch (error) {
          console.error('Failed to update goals:', error);
          throw error;
        }
      },

      clearError: () => set({ error: null }),

      setTokens: (tokens: AuthTokens) => {
        authService.setTokens(tokens);
        set({ isAuthenticated: true });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
);
