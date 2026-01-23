import { create } from 'zustand';
import type { WaterLog, DailyWaterSummary, ContainerType } from '@/types';
import { waterService, WaterLogData } from '@/services/waterService';
import { format } from 'date-fns';

interface WaterState {
  // Data
  selectedDate: string;
  dailyLogs: WaterLog[];
  dailySummary: DailyWaterSummary | null;
  dailyGoal: number;
  
  // Loading states
  isLoading: boolean;
  isLogging: boolean;
  
  // Actions
  setSelectedDate: (date: string) => void;
  loadDailyData: (date?: string) => Promise<void>;
  logWater: (data: WaterLogData) => Promise<WaterLog>;
  quickAddWater: (containerType: ContainerType) => Promise<void>;
  deleteWaterLog: (id: number) => Promise<void>;
  updateGoal: (goalMl: number) => Promise<void>;
}

export const useWaterStore = create<WaterState>((set, get) => ({
  selectedDate: format(new Date(), 'yyyy-MM-dd'),
  dailyLogs: [],
  dailySummary: null,
  dailyGoal: 2000,
  isLoading: false,
  isLogging: false,

  setSelectedDate: (date: string) => {
    set({ selectedDate: date });
    get().loadDailyData(date);
  },

  loadDailyData: async (date?: string) => {
    const targetDate = date || get().selectedDate;
    set({ isLoading: true });
    
    try {
      const [logs, summary] = await Promise.all([
        waterService.getDailyLogs(targetDate),
        waterService.getDailySummary(targetDate),
      ]);
      
      set({ 
        dailyLogs: logs, 
        dailySummary: summary,
        dailyGoal: summary.goal_ml,
        isLoading: false 
      });
    } catch (error) {
      console.error('Failed to load water data:', error);
      set({ isLoading: false });
    }
  },

  logWater: async (data: WaterLogData) => {
    set({ isLogging: true });
    try {
      const log = await waterService.logWater(data);
      await get().loadDailyData();
      set({ isLogging: false });
      return log;
    } catch (error) {
      set({ isLogging: false });
      throw error;
    }
  },

  quickAddWater: async (containerType: ContainerType) => {
    const date = get().selectedDate;
    set({ isLogging: true });
    try {
      await waterService.quickAddWater(containerType, date);
      await get().loadDailyData();
      set({ isLogging: false });
    } catch (error) {
      set({ isLogging: false });
      throw error;
    }
  },

  deleteWaterLog: async (id: number) => {
    try {
      await waterService.deleteWaterLog(id);
      await get().loadDailyData();
    } catch (error) {
      console.error('Failed to delete water log:', error);
      throw error;
    }
  },

  updateGoal: async (goalMl: number) => {
    try {
      await waterService.updateGoal({ daily_goal_ml: goalMl });
      set({ dailyGoal: goalMl });
      await get().loadDailyData();
    } catch (error) {
      console.error('Failed to update water goal:', error);
      throw error;
    }
  },
}));
