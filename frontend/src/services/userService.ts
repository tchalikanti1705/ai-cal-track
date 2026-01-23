import api from './api';
import type { 
  UserProfile, 
  UserGoals, 
  ApiResponse 
} from '@/types';

export interface ProfileUpdateData {
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  gender?: string;
  height_cm?: number;
  current_weight_kg?: number;
  target_weight_kg?: number;
  activity_level?: string;
  dietary_preference?: string;
  allergies?: string[];
  health_conditions?: string[];
  timezone?: string;
  measurement_system?: string;
}

export interface GoalsUpdateData {
  goal_type?: string;
  daily_calorie_goal?: number;
  is_calorie_goal_custom?: boolean;
  protein_goal_g?: number;
  carbs_goal_g?: number;
  fat_goal_g?: number;
  water_goal_ml?: number;
  weekly_exercise_minutes?: number;
  daily_steps_goal?: number;
  weekly_workout_days?: number;
  weight_goal_kg?: number;
  weight_change_rate?: number;
  track_calories?: boolean;
  track_macros?: boolean;
  track_water?: boolean;
  track_exercise?: boolean;
  track_steps?: boolean;
}

export interface OnboardingStep {
  step: number;
  question_key: string;
  question_text: string;
  response_value: string;
  response_metadata?: Record<string, unknown>;
}

export const userService = {
  async getProfile(): Promise<UserProfile> {
    const response = await api.get<ApiResponse<UserProfile>>('/users/profile');
    return response.data.data;
  },

  async updateProfile(data: ProfileUpdateData): Promise<UserProfile> {
    const response = await api.put<ApiResponse<UserProfile>>('/users/profile', data);
    return response.data.data;
  },

  async getGoals(): Promise<UserGoals> {
    const response = await api.get<ApiResponse<UserGoals>>('/users/goals');
    return response.data.data;
  },

  async updateGoals(data: GoalsUpdateData): Promise<UserGoals> {
    const response = await api.put<ApiResponse<UserGoals>>('/users/goals', data);
    return response.data.data;
  },

  async calculateGoals(): Promise<UserGoals> {
    const response = await api.post<ApiResponse<UserGoals>>('/users/goals/calculate');
    return response.data.data;
  },

  async submitOnboardingStep(data: OnboardingStep): Promise<{ step: number; completed: boolean }> {
    const response = await api.post<ApiResponse<{ step: number; completed: boolean }>>('/users/onboarding', data);
    return response.data.data;
  },

  async completeOnboarding(): Promise<void> {
    await api.post('/users/onboarding/complete');
  },

  async getOnboardingResponses(): Promise<OnboardingStep[]> {
    const response = await api.get<ApiResponse<OnboardingStep[]>>('/users/onboarding/responses');
    return response.data.data;
  },
};

export default userService;
