import api from './api';
import type { 
  Exercise, 
  ExerciseLog, 
  ExerciseCategory,
  ExerciseIntensity,
  ApiResponse,
  ApiListResponse
} from '@/types';

export interface ExerciseLogData {
  exercise_type_id?: number;
  log_date: string;
  start_time?: string;
  end_time?: string;
  duration_minutes: number;
  exercise_name: string;
  category: ExerciseCategory;
  intensity?: ExerciseIntensity;
  calories_burned?: number;
  is_calories_manual?: boolean;
  distance_km?: number;
  notes?: string;
}

export const exerciseService = {
  // Exercise Library
  async getExercises(category?: ExerciseCategory): Promise<Exercise[]> {
    const response = await api.get<ApiListResponse<Exercise>>('/exercises/library', {
      params: category ? { category } : undefined,
    });
    return response.data.data;
  },

  async searchExercises(query: string): Promise<Exercise[]> {
    const response = await api.get<ApiListResponse<Exercise>>('/exercises/search', {
      params: { query },
    });
    return response.data.data;
  },

  async getExerciseById(id: number): Promise<Exercise> {
    const response = await api.get<ApiResponse<Exercise>>(`/exercises/${id}`);
    return response.data.data;
  },

  // Exercise Logging
  async logExercise(data: ExerciseLogData): Promise<ExerciseLog> {
    const response = await api.post<ApiResponse<ExerciseLog>>('/exercises/log', data);
    return response.data.data;
  },

  async updateExerciseLog(id: number, data: Partial<ExerciseLogData>): Promise<ExerciseLog> {
    const response = await api.put<ApiResponse<ExerciseLog>>(`/exercises/log/${id}`, data);
    return response.data.data;
  },

  async deleteExerciseLog(id: number): Promise<void> {
    await api.delete(`/exercises/log/${id}`);
  },

  // Get logs
  async getDailyLogs(date: string): Promise<ExerciseLog[]> {
    const response = await api.get<ApiListResponse<ExerciseLog>>('/exercises/log', {
      params: { date },
    });
    return response.data.data;
  },

  async getWeeklyLogs(startDate: string): Promise<ExerciseLog[]> {
    const response = await api.get<ApiListResponse<ExerciseLog>>('/exercises/log/weekly', {
      params: { start_date: startDate },
    });
    return response.data.data;
  },

  // Summaries
  async getDailySummary(date: string): Promise<{
    date: string;
    total_duration_minutes: number;
    total_calories_burned: number;
    sessions_count: number;
    categories: Record<ExerciseCategory, { minutes: number; calories: number }>;
    logs: ExerciseLog[];
  }> {
    const response = await api.get<ApiResponse<{
      date: string;
      total_duration_minutes: number;
      total_calories_burned: number;
      sessions_count: number;
      categories: Record<ExerciseCategory, { minutes: number; calories: number }>;
      logs: ExerciseLog[];
    }>>('/exercises/summary/daily', {
      params: { date },
    });
    return response.data.data;
  },

  async getWeeklySummary(startDate: string): Promise<{
    week_start: string;
    week_end: string;
    total_duration_minutes: number;
    total_calories_burned: number;
    sessions_count: number;
    goal_minutes: number;
    goal_percent: number;
    daily_breakdown: Array<{ date: string; minutes: number; calories: number }>;
  }> {
    const response = await api.get<ApiResponse<{
      week_start: string;
      week_end: string;
      total_duration_minutes: number;
      total_calories_burned: number;
      sessions_count: number;
      goal_minutes: number;
      goal_percent: number;
      daily_breakdown: Array<{ date: string; minutes: number; calories: number }>;
    }>>('/exercises/summary/weekly', {
      params: { start_date: startDate },
    });
    return response.data.data;
  },

  // Utilities
  calculateCaloriesBurned(metValue: number, durationMinutes: number, weightKg: number): number {
    // Calories burned = MET × weight (kg) × duration (hours)
    const durationHours = durationMinutes / 60;
    return Math.round(metValue * weightKg * durationHours);
  },
};

export default exerciseService;
