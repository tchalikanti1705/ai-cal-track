import api from './api';
import type { 
  DashboardData, 
  WeeklyTrend, 
  InsightRecommendation,
  ApiResponse 
} from '@/types';

export const insightsService = {
  // Dashboard
  async getDashboard(): Promise<DashboardData> {
    const response = await api.get<DashboardData>('/insights/dashboard');
    return response.data;
  },

  // Trends
  async getWeeklyTrends(startDate?: string): Promise<WeeklyTrend> {
    const response = await api.get<WeeklyTrend>('/insights/trends/weekly', {
      params: startDate ? { start_date: startDate } : undefined,
    });
    return response.data;
  },

  async getMonthlyTrends(month?: number, year?: number): Promise<{
    month: number;
    year: number;
    calories: { daily_average: number; goal_met_days: number; total: number };
    water: { daily_average_ml: number; goal_met_days: number };
    steps: { daily_average: number; goal_met_days: number; total: number };
    exercise: { total_minutes: number; sessions: number; weekly_avg: number };
    weight: { start_kg: number | null; end_kg: number | null; change_kg: number | null };
    weekly_breakdown: WeeklyTrend[];
  }> {
    const response = await api.get<ApiResponse<{
      month: number;
      year: number;
      calories: { daily_average: number; goal_met_days: number; total: number };
      water: { daily_average_ml: number; goal_met_days: number };
      steps: { daily_average: number; goal_met_days: number; total: number };
      exercise: { total_minutes: number; sessions: number; weekly_avg: number };
      weight: { start_kg: number | null; end_kg: number | null; change_kg: number | null };
      weekly_breakdown: WeeklyTrend[];
    }>>('/insights/trends/monthly', {
      params: { month, year },
    });
    return response.data.data;
  },

  // Recommendations
  async getRecommendations(): Promise<InsightRecommendation[]> {
    const response = await api.get<InsightRecommendation[]>('/insights/recommendations');
    return response.data;
  },

  // Progress
  async getProgress(period: 'week' | 'month' | 'year' = 'week'): Promise<{
    period: string;
    goals_summary: {
      calorie_goal_met_days: number;
      water_goal_met_days: number;
      step_goal_met_days: number;
      exercise_goal_met_days: number;
      total_days: number;
    };
    trends: {
      calories: 'improving' | 'stable' | 'declining';
      water: 'improving' | 'stable' | 'declining';
      steps: 'improving' | 'stable' | 'declining';
      exercise: 'improving' | 'stable' | 'declining';
    };
    achievements: Array<{
      id: string;
      title: string;
      description: string;
      earned_at: string;
    }>;
  }> {
    const response = await api.get<ApiResponse<{
      period: string;
      goals_summary: {
        calorie_goal_met_days: number;
        water_goal_met_days: number;
        step_goal_met_days: number;
        exercise_goal_met_days: number;
        total_days: number;
      };
      trends: {
        calories: 'improving' | 'stable' | 'declining';
        water: 'improving' | 'stable' | 'declining';
        steps: 'improving' | 'stable' | 'declining';
        exercise: 'improving' | 'stable' | 'declining';
      };
      achievements: Array<{
        id: string;
        title: string;
        description: string;
        earned_at: string;
      }>;
    }>>('/insights/progress', {
      params: { period },
    });
    return response.data.data;
  },

  // Weight tracking
  async getWeightHistory(days = 30): Promise<Array<{
    date: string;
    weight_kg: number;
  }>> {
    const response = await api.get<ApiResponse<Array<{
      date: string;
      weight_kg: number;
    }>>>('/insights/weight-history', {
      params: { days },
    });
    return response.data.data;
  },
};

export default insightsService;
