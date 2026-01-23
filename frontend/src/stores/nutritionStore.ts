import { create } from 'zustand';
import type { NutritionLog, DailyNutritionSummary, MealType, FoodEntry } from '@/types';
import { nutritionService, FoodLogData } from '@/services/nutritionService';
import { format } from 'date-fns';

interface NutritionState {
  // Data
  selectedDate: string;
  dailyLogs: NutritionLog[];
  dailySummary: DailyNutritionSummary | null;
  searchResults: FoodEntry[];
  recentFoods: FoodEntry[];
  
  // Loading states
  isLoading: boolean;
  isSearching: boolean;
  isLogging: boolean;
  
  // Actions
  setSelectedDate: (date: string) => void;
  loadDailyData: (date?: string) => Promise<void>;
  searchFoods: (query: string) => Promise<void>;
  logFood: (data: FoodLogData) => Promise<NutritionLog>;
  updateFoodLog: (id: number, data: Partial<FoodLogData>) => Promise<void>;
  deleteFoodLog: (id: number) => Promise<void>;
  quickAddCalories: (calories: number, mealType: MealType) => Promise<void>;
  clearSearch: () => void;
}

export const useNutritionStore = create<NutritionState>((set, get) => ({
  selectedDate: format(new Date(), 'yyyy-MM-dd'),
  dailyLogs: [],
  dailySummary: null,
  searchResults: [],
  recentFoods: [],
  isLoading: false,
  isSearching: false,
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
        nutritionService.getDailyLogs(targetDate),
        nutritionService.getDailySummary(targetDate),
      ]);
      
      set({ 
        dailyLogs: logs, 
        dailySummary: summary, 
        isLoading: false 
      });
    } catch (error) {
      console.error('Failed to load nutrition data:', error);
      set({ isLoading: false });
    }
  },

  searchFoods: async (query: string) => {
    if (!query.trim()) {
      set({ searchResults: [] });
      return;
    }

    set({ isSearching: true });
    try {
      const results = await nutritionService.searchFoods(query);
      set({ searchResults: results, isSearching: false });
    } catch (error) {
      console.error('Search failed:', error);
      set({ isSearching: false });
    }
  },

  logFood: async (data: FoodLogData) => {
    set({ isLogging: true });
    try {
      const log = await nutritionService.logFood(data);
      
      // Refresh daily data
      await get().loadDailyData();
      
      set({ isLogging: false });
      return log;
    } catch (error) {
      set({ isLogging: false });
      throw error;
    }
  },

  updateFoodLog: async (id: number, data: Partial<FoodLogData>) => {
    try {
      await nutritionService.updateFoodLog(id, data);
      await get().loadDailyData();
    } catch (error) {
      console.error('Failed to update food log:', error);
      throw error;
    }
  },

  deleteFoodLog: async (id: number) => {
    try {
      await nutritionService.deleteFoodLog(id);
      await get().loadDailyData();
    } catch (error) {
      console.error('Failed to delete food log:', error);
      throw error;
    }
  },

  quickAddCalories: async (calories: number, mealType: MealType) => {
    const date = get().selectedDate;
    try {
      await nutritionService.quickAddCalories(calories, mealType, date);
      await get().loadDailyData();
    } catch (error) {
      console.error('Failed to quick add calories:', error);
      throw error;
    }
  },

  clearSearch: () => set({ searchResults: [] }),
}));
