// User Types
export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface UserProfile {
  id: number;
  user_id: number;
  first_name: string | null;
  last_name: string | null;
  date_of_birth: string | null;
  gender: 'male' | 'female' | 'other' | 'prefer_not_to_say' | null;
  height_cm: number | null;
  current_weight_kg: number | null;
  target_weight_kg: number | null;
  activity_level: ActivityLevel;
  dietary_preference: DietaryPreference;
  allergies: string[];
  health_conditions: string[];
  timezone: string;
  measurement_system: 'metric' | 'imperial';
  profile_image_url: string | null;
  onboarding_completed: boolean;
  onboarding_step: number;
}

export interface UserGoals {
  id: number;
  user_id: number;
  goal_type: GoalType;
  daily_calorie_goal: number;
  is_calorie_goal_custom: boolean;
  protein_goal_g: number;
  carbs_goal_g: number;
  fat_goal_g: number;
  fiber_goal_g: number;
  sodium_limit_mg: number;
  sugar_limit_g: number;
  water_goal_ml: number;
  weekly_exercise_minutes: number;
  daily_steps_goal: number;
  weekly_workout_days: number;
  weight_goal_kg: number | null;
  weight_change_rate: number;
  track_calories: boolean;
  track_macros: boolean;
  track_water: boolean;
  track_exercise: boolean;
  track_steps: boolean;
}

export type ActivityLevel = 
  | 'sedentary'
  | 'lightly_active'
  | 'moderately_active'
  | 'very_active'
  | 'extremely_active';

export type DietaryPreference =
  | 'none'
  | 'vegetarian'
  | 'vegan'
  | 'pescatarian'
  | 'keto'
  | 'paleo'
  | 'mediterranean'
  | 'halal'
  | 'kosher';

export type GoalType = 
  | 'lose_weight'
  | 'gain_weight'
  | 'maintain_weight'
  | 'build_muscle'
  | 'improve_health';

// Auth Types
export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

// Nutrition Types
export interface FoodEntry {
  id: number;
  name: string;
  brand: string | null;
  barcode: string | null;
  serving_size: number;
  serving_unit: string;
  calories: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
  fiber_g: number;
  sugar_g: number;
  category: string | null;
}

export interface NutritionLog {
  id: number;
  user_id: number;
  food_entry_id: number | null;
  log_date: string;
  log_time: string;
  meal_type: MealType;
  food_name: string;
  brand: string | null;
  quantity: number;
  serving_size: number;
  serving_unit: string;
  calories: number;
  protein_g: number;
  carbohydrates_g: number;
  fat_g: number;
  fiber_g: number;
  sugar_g: number;
  source: string;
  notes: string | null;
}

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snacks';

export interface DailyNutritionSummary {
  date: string;
  total_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
  total_fiber_g: number;
  total_sugar_g: number;
  calorie_goal: number;
  calorie_goal_percent: number;
  meals: {
    [key in MealType]: {
      calories: number;
      items: NutritionLog[];
    };
  };
}

// Exercise Types
export interface Exercise {
  id: number;
  name: string;
  category: ExerciseCategory;
  description: string | null;
  met_value: number;
  typical_duration_minutes: number;
  image_url: string | null;
}

export interface ExerciseLog {
  id: number;
  user_id: number;
  exercise_type_id: number | null;
  log_date: string;
  start_time: string | null;
  end_time: string | null;
  duration_minutes: number;
  exercise_name: string;
  category: string;
  intensity: ExerciseIntensity;
  calories_burned: number;
  is_calories_manual: boolean;
  distance_km: number | null;
  notes: string | null;
}

export type ExerciseCategory = 
  | 'cardio'
  | 'strength'
  | 'flexibility'
  | 'sports'
  | 'walking'
  | 'running'
  | 'cycling'
  | 'swimming'
  | 'yoga'
  | 'hiit';

export type ExerciseIntensity = 'light' | 'moderate' | 'vigorous' | 'maximum';

// Water Types
export interface WaterLog {
  id: number;
  user_id: number;
  log_date: string;
  log_time: string;
  amount_ml: number;
  container_type: ContainerType;
  beverage_type: string;
}

export interface WaterGoal {
  id: number;
  user_id: number;
  daily_goal_ml: number;
  reminder_enabled: boolean;
  reminder_interval_minutes: number;
  effective_from: string;
}

export interface DailyWaterSummary {
  date: string;
  total_ml: number;
  goal_ml: number;
  goal_percent: number;
  entries_count: number;
  entries: WaterLog[];
}

export type ContainerType = 
  | 'glass'
  | 'small_bottle'
  | 'large_bottle'
  | 'cup'
  | 'mug'
  | 'custom';

// Walking Types
export interface WalkingSession {
  id: number;
  user_id: number;
  session_date: string;
  start_time: string;
  end_time: string | null;
  duration_minutes: number;
  steps: number;
  distance_meters: number | null;
  calories_burned: number | null;
  avg_pace_min_per_km: number | null;
  activity_type: string;
  title: string | null;
  notes: string | null;
}

export interface StepCount {
  id: number;
  user_id: number;
  count_date: string;
  total_steps: number;
  step_goal: number;
  goal_achieved: boolean;
  total_distance_meters: number | null;
  total_calories_burned: number | null;
  active_minutes: number;
}

export interface DailyStepsSummary {
  date: string;
  total_steps: number;
  step_goal: number;
  goal_percent: number;
  distance_km: number;
  calories_burned: number;
  active_minutes: number;
  sessions: WalkingSession[];
}

// Food Scan Types
export interface FoodScan {
  id: number;
  user_id: number;
  scan_type: 'photo' | 'barcode';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  image_url: string | null;
  barcode: string | null;
  scanned_at: string;
  processed_at: string | null;
  confidence_score: number | null;
}

export interface FoodScanResult {
  id: number;
  scan_id: number;
  food_name: string;
  brand: string | null;
  confidence: number;
  estimated_portion: string | null;
  estimated_weight_g: number | null;
  estimated_calories: number | null;
  estimated_protein_g: number | null;
  estimated_carbs_g: number | null;
  estimated_fat_g: number | null;
  added_to_log: boolean;
}

// Insights Types
export interface DashboardData {
  date: string;
  nutrition: {
    calories: { consumed: number; goal: number; remaining: number; percent: number };
    protein: { consumed: number; goal: number; percent: number };
    carbs: { consumed: number; goal: number; percent: number };
    fat: { consumed: number; goal: number; percent: number };
    meals_logged: number;
  };
  water: { consumed: number; goal: number; remaining: number; percent: number; entries: number };
  exercise: { calories_burned: number; minutes: number; workouts: number };
  steps: { count: number; goal: number; percent: number };
  net_calories: number;
}

export interface WeeklyTrend {
  week_start: string;
  week_end: string;
  calories: { daily: number[]; average: number; goal_met_days: number };
  water: { daily: number[]; average: number; goal_met_days: number };
  steps: { daily: number[]; average: number; goal_met_days: number };
  exercise: { daily_minutes: number[]; total_minutes: number; sessions: number };
  weight: { start_kg: number | null; end_kg: number | null; change_kg: number | null };
}

export interface InsightRecommendation {
  id: string;
  type: 'nutrition' | 'hydration' | 'exercise' | 'general';
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high';
  action_label?: string;
  action_route?: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface ApiListResponse<T> {
  success: boolean;
  message: string;
  data: T[];
  total?: number;
  page?: number;
  page_size?: number;
}

export interface ApiError {
  success: false;
  message: string;
  error_code: string;
  details?: string[];
}
