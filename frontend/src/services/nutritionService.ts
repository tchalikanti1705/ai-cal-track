import api from './api';
import type { 
  FoodEntry, 
  NutritionLog, 
  DailyNutritionSummary,
  MealType,
  ApiResponse,
  ApiListResponse
} from '@/types';

export interface FoodLogData {
  food_entry_id?: number;
  log_date: string;
  meal_type: MealType;
  food_name: string;
  brand?: string;
  quantity: number;
  serving_size: number;
  serving_unit: string;
  calories: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
  fiber_g?: number;
  sugar_g?: number;
  sodium_mg?: number;
  source?: string;
  notes?: string;
}

export const nutritionService = {
  // Food Search
  async searchFoods(query: string, limit = 20): Promise<FoodEntry[]> {
    const response = await api.get<ApiListResponse<FoodEntry>>('/nutrition/foods/search', {
      params: { query, limit },
    });
    return response.data.data;
  },

  async getFoodByBarcode(barcode: string): Promise<FoodEntry | null> {
    try {
      const response = await api.get<ApiResponse<FoodEntry>>(`/nutrition/foods/barcode/${barcode}`);
      return response.data.data;
    } catch {
      return null;
    }
  },

  async getFoodById(id: number): Promise<FoodEntry> {
    const response = await api.get<ApiResponse<FoodEntry>>(`/nutrition/foods/${id}`);
    return response.data.data;
  },

  // Food Logging
  async logFood(data: FoodLogData): Promise<NutritionLog> {
    const response = await api.post<ApiResponse<NutritionLog>>('/nutrition/log', data);
    return response.data.data;
  },

  async updateFoodLog(id: number, data: Partial<FoodLogData>): Promise<NutritionLog> {
    const response = await api.put<ApiResponse<NutritionLog>>(`/nutrition/log/${id}`, data);
    return response.data.data;
  },

  async deleteFoodLog(id: number): Promise<void> {
    await api.delete(`/nutrition/log/${id}`);
  },

  // Get logs
  async getDailyLogs(date: string): Promise<NutritionLog[]> {
    const response = await api.get<ApiListResponse<NutritionLog>>('/nutrition/log', {
      params: { date },
    });
    return response.data.data;
  },

  async getMealLogs(date: string, mealType: MealType): Promise<NutritionLog[]> {
    const response = await api.get<ApiListResponse<NutritionLog>>(`/nutrition/log/meal/${mealType}`, {
      params: { date },
    });
    return response.data.data;
  },

  // Summaries
  async getDailySummary(date: string): Promise<DailyNutritionSummary> {
    const response = await api.get<ApiResponse<DailyNutritionSummary>>('/nutrition/summary/daily', {
      params: { date },
    });
    return response.data.data;
  },

  async getWeeklySummary(startDate: string): Promise<DailyNutritionSummary[]> {
    const response = await api.get<ApiListResponse<DailyNutritionSummary>>('/nutrition/summary/weekly', {
      params: { start_date: startDate },
    });
    return response.data.data;
  },

  async getMacroBreakdown(date: string): Promise<{
    protein: { grams: number; goal: number; percent: number; calories: number };
    carbs: { grams: number; goal: number; percent: number; calories: number };
    fat: { grams: number; goal: number; percent: number; calories: number };
    fiber: { grams: number; goal: number; percent: number };
    sugar: { grams: number; limit: number; percent: number };
  }> {
    const response = await api.get<ApiResponse<{
      protein: { grams: number; goal: number; percent: number; calories: number };
      carbs: { grams: number; goal: number; percent: number; calories: number };
      fat: { grams: number; goal: number; percent: number; calories: number };
      fiber: { grams: number; goal: number; percent: number };
      sugar: { grams: number; limit: number; percent: number };
    }>>('/nutrition/macros', {
      params: { date },
    });
    return response.data.data;
  },

  // Quick add
  async quickAddCalories(calories: number, mealType: MealType, date: string): Promise<NutritionLog> {
    const response = await api.post<ApiResponse<NutritionLog>>('/nutrition/quick-add', {
      calories,
      meal_type: mealType,
      log_date: date,
    });
    return response.data.data;
  },
};

export default nutritionService;
