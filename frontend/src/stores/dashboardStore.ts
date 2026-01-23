import { create } from 'zustand';
import type { DashboardData, WeeklyTrend, InsightRecommendation } from '@/types';
import { insightsService } from '@/services';

interface DashboardState {
  // Data
  dashboard: DashboardData | null;
  weeklyTrends: WeeklyTrend | null;
  recommendations: InsightRecommendation[];
  
  // Loading states
  isLoading: boolean;
  isTrendsLoading: boolean;
  
  // Actions
  loadDashboard: () => Promise<void>;
  loadWeeklyTrends: (startDate?: string) => Promise<void>;
  loadRecommendations: () => Promise<void>;
  refreshAll: () => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  dashboard: null,
  weeklyTrends: null,
  recommendations: [],
  isLoading: false,
  isTrendsLoading: false,

  loadDashboard: async () => {
    set({ isLoading: true });
    try {
      const dashboard = await insightsService.getDashboard();
      set({ dashboard, isLoading: false });
    } catch (error) {
      console.error('Failed to load dashboard:', error);
      set({ isLoading: false });
    }
  },

  loadWeeklyTrends: async (startDate?: string) => {
    set({ isTrendsLoading: true });
    try {
      const trends = await insightsService.getWeeklyTrends(startDate);
      set({ weeklyTrends: trends, isTrendsLoading: false });
    } catch (error) {
      console.error('Failed to load trends:', error);
      set({ isTrendsLoading: false });
    }
  },

  loadRecommendations: async () => {
    try {
      const recommendations = await insightsService.getRecommendations();
      set({ recommendations });
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    }
  },

  refreshAll: async () => {
    const { loadDashboard, loadWeeklyTrends, loadRecommendations } = get();
    await Promise.all([
      loadDashboard(),
      loadWeeklyTrends(),
      loadRecommendations(),
    ]);
  },
}));
