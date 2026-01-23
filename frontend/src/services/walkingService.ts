import api from './api';
import type { 
  WalkingSession, 
  StepCount, 
  DailyStepsSummary,
  ApiResponse,
  ApiListResponse
} from '@/types';

export interface WalkingSessionData {
  session_date: string;
  start_time: string;
  end_time?: string;
  duration_minutes?: number;
  steps?: number;
  distance_meters?: number;
  calories_burned?: number;
  activity_type?: string;
  title?: string;
  notes?: string;
  is_outdoor?: boolean;
}

export interface StepCountData {
  count_date: string;
  total_steps: number;
  step_goal?: number;
}

export const walkingService = {
  // Walking Sessions
  async startSession(data: { session_date: string; start_time: string }): Promise<WalkingSession> {
    const response = await api.post<ApiResponse<WalkingSession>>('/walking/sessions/start', data);
    return response.data.data;
  },

  async endSession(id: number, data: { 
    end_time: string; 
    steps?: number; 
    distance_meters?: number;
  }): Promise<WalkingSession> {
    const response = await api.post<ApiResponse<WalkingSession>>(`/walking/sessions/${id}/end`, data);
    return response.data.data;
  },

  async logSession(data: WalkingSessionData): Promise<WalkingSession> {
    const response = await api.post<ApiResponse<WalkingSession>>('/walking/sessions', data);
    return response.data.data;
  },

  async updateSession(id: number, data: Partial<WalkingSessionData>): Promise<WalkingSession> {
    const response = await api.put<ApiResponse<WalkingSession>>(`/walking/sessions/${id}`, data);
    return response.data.data;
  },

  async deleteSession(id: number): Promise<void> {
    await api.delete(`/walking/sessions/${id}`);
  },

  async getDailySessions(date: string): Promise<WalkingSession[]> {
    const response = await api.get<ApiListResponse<WalkingSession>>('/walking/sessions', {
      params: { date },
    });
    return response.data.data;
  },

  // Step Counts
  async logSteps(data: StepCountData): Promise<StepCount> {
    const response = await api.post<ApiResponse<StepCount>>('/walking/steps', data);
    return response.data.data;
  },

  async updateSteps(date: string, steps: number): Promise<StepCount> {
    const response = await api.put<ApiResponse<StepCount>>(`/walking/steps/${date}`, {
      total_steps: steps,
    });
    return response.data.data;
  },

  async getDailySteps(date: string): Promise<StepCount | null> {
    try {
      const response = await api.get<ApiResponse<StepCount>>(`/walking/steps/${date}`);
      return response.data.data;
    } catch {
      return null;
    }
  },

  // Summaries
  async getDailySummary(date: string): Promise<DailyStepsSummary> {
    const response = await api.get<ApiResponse<DailyStepsSummary>>('/walking/summary/daily', {
      params: { date },
    });
    return response.data.data;
  },

  async getWeeklySummary(startDate: string): Promise<{
    week_start: string;
    week_end: string;
    total_steps: number;
    daily_average: number;
    step_goal: number;
    goal_met_days: number;
    total_distance_km: number;
    total_calories_burned: number;
    total_active_minutes: number;
    daily_breakdown: Array<{ 
      date: string; 
      steps: number; 
      goal_percent: number; 
      distance_km: number;
    }>;
  }> {
    const response = await api.get<ApiResponse<{
      week_start: string;
      week_end: string;
      total_steps: number;
      daily_average: number;
      step_goal: number;
      goal_met_days: number;
      total_distance_km: number;
      total_calories_burned: number;
      total_active_minutes: number;
      daily_breakdown: Array<{ 
        date: string; 
        steps: number; 
        goal_percent: number; 
        distance_km: number;
      }>;
    }>>('/walking/summary/weekly', {
      params: { start_date: startDate },
    });
    return response.data.data;
  },

  // Utilities
  calculateCaloriesFromSteps(steps: number, weightKg: number): number {
    // Average calories burned per step is about 0.04-0.06 per kg body weight
    return Math.round(steps * 0.05 * (weightKg / 70));
  },

  calculateDistanceFromSteps(steps: number, heightCm: number): number {
    // Average stride length is about 0.415 x height
    const strideLengthM = (0.415 * heightCm) / 100;
    return steps * strideLengthM;
  },
};

export default walkingService;
