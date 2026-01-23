import api from './api';
import type { 
  WaterLog, 
  WaterGoal, 
  DailyWaterSummary,
  ContainerType,
  ApiResponse,
  ApiListResponse
} from '@/types';

export interface WaterLogData {
  log_date: string;
  log_time?: string;
  amount_ml: number;
  container_type?: ContainerType;
  beverage_type?: string;
}

export interface WaterGoalData {
  daily_goal_ml: number;
  reminder_enabled?: boolean;
  reminder_interval_minutes?: number;
  reminder_start_time?: string;
  reminder_end_time?: string;
}

export const CONTAINER_SIZES: Record<ContainerType, number> = {
  glass: 250,
  small_bottle: 330,
  large_bottle: 500,
  cup: 200,
  mug: 350,
  custom: 0,
};

export const waterService = {
  // Water Logging
  async logWater(data: WaterLogData): Promise<WaterLog> {
    const response = await api.post<ApiResponse<WaterLog>>('/water/log', data);
    return response.data.data;
  },

  async updateWaterLog(id: number, data: Partial<WaterLogData>): Promise<WaterLog> {
    const response = await api.put<ApiResponse<WaterLog>>(`/water/log/${id}`, data);
    return response.data.data;
  },

  async deleteWaterLog(id: number): Promise<void> {
    await api.delete(`/water/log/${id}`);
  },

  // Quick add with preset containers
  async quickAddWater(containerType: ContainerType, date: string): Promise<WaterLog> {
    const amount = CONTAINER_SIZES[containerType];
    return this.logWater({
      log_date: date,
      amount_ml: amount,
      container_type: containerType,
      beverage_type: 'water',
    });
  },

  // Get logs
  async getDailyLogs(date: string): Promise<WaterLog[]> {
    const response = await api.get<ApiListResponse<WaterLog>>('/water/log', {
      params: { date },
    });
    return response.data.data;
  },

  // Summaries
  async getDailySummary(date: string): Promise<DailyWaterSummary> {
    const response = await api.get<ApiResponse<DailyWaterSummary>>('/water/summary/daily', {
      params: { date },
    });
    return response.data.data;
  },

  async getWeeklySummary(startDate: string): Promise<{
    week_start: string;
    week_end: string;
    total_ml: number;
    daily_average_ml: number;
    goal_ml: number;
    goal_met_days: number;
    daily_breakdown: Array<{ date: string; total_ml: number; goal_percent: number }>;
  }> {
    const response = await api.get<ApiResponse<{
      week_start: string;
      week_end: string;
      total_ml: number;
      daily_average_ml: number;
      goal_ml: number;
      goal_met_days: number;
      daily_breakdown: Array<{ date: string; total_ml: number; goal_percent: number }>;
    }>>('/water/summary/weekly', {
      params: { start_date: startDate },
    });
    return response.data.data;
  },

  // Goals
  async getGoal(): Promise<WaterGoal> {
    const response = await api.get<ApiResponse<WaterGoal>>('/water/goal');
    return response.data.data;
  },

  async updateGoal(data: WaterGoalData): Promise<WaterGoal> {
    const response = await api.put<ApiResponse<WaterGoal>>('/water/goal', data);
    return response.data.data;
  },

  // Container presets
  getContainerPresets(): Array<{ type: ContainerType; label: string; amount_ml: number; icon: string }> {
    return [
      { type: 'glass', label: 'Glass', amount_ml: 250, icon: '🥛' },
      { type: 'cup', label: 'Cup', amount_ml: 200, icon: '☕' },
      { type: 'mug', label: 'Mug', amount_ml: 350, icon: '🍵' },
      { type: 'small_bottle', label: 'Small Bottle', amount_ml: 330, icon: '🍶' },
      { type: 'large_bottle', label: 'Large Bottle', amount_ml: 500, icon: '🧴' },
    ];
  },
};

export default waterService;
