import React, { useEffect, useState } from 'react';
import { format, addDays, subDays } from 'date-fns';
import { useNutritionStore, useAuthStore } from '@/stores';
import { Card, CardHeader, Button, Input, ProgressRing, LoadingSpinner } from '@/components/ui';
import { MealType, NutritionLog } from '@/types';
import {
  PlusIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  MagnifyingGlassIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const mealTypes: { key: MealType; label: string; icon: string }[] = [
  { key: 'breakfast', label: 'Breakfast', icon: '🌅' },
  { key: 'lunch', label: 'Lunch', icon: '☀️' },
  { key: 'dinner', label: 'Dinner', icon: '🌙' },
  { key: 'snacks', label: 'Snacks', icon: '🍿' },
];

export const NutritionPage: React.FC = () => {
  const { goals } = useAuthStore();
  const {
    selectedDate,
    setSelectedDate,
    dailyLogs,
    dailySummary,
    searchResults,
    isLoading,
    isSearching,
    loadDailyData,
    searchFoods,
    logFood,
    deleteFoodLog,
    clearSearch,
  } = useNutritionStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMeal, setSelectedMeal] = useState<MealType | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    loadDailyData();
  }, [loadDailyData]);

  const handleDateChange = (direction: 'prev' | 'next') => {
    const currentDate = new Date(selectedDate);
    const newDate = direction === 'prev' 
      ? subDays(currentDate, 1) 
      : addDays(currentDate, 1);
    setSelectedDate(format(newDate, 'yyyy-MM-dd'));
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      searchFoods(query);
    } else {
      clearSearch();
    }
  };

  const handleAddFood = async (food: typeof searchResults[0]) => {
    if (!selectedMeal) return;

    try {
      await logFood({
        food_entry_id: food.id,
        log_date: selectedDate,
        meal_type: selectedMeal,
        food_name: food.name,
        brand: food.brand || undefined,
        quantity: 1,
        serving_size: food.serving_size,
        serving_unit: food.serving_unit,
        calories: food.calories,
        protein_g: food.protein_g,
        carbohydrates_g: food.carbohydrates_g,
        fat_g: food.fat_g,
        fiber_g: food.fiber_g,
        sugar_g: food.sugar_g,
      });
      toast.success('Food added successfully');
      setShowAddModal(false);
      setSearchQuery('');
      clearSearch();
    } catch {
      toast.error('Failed to add food');
    }
  };

  const handleDeleteLog = async (id: number) => {
    if (!confirm('Are you sure you want to delete this entry?')) return;
    try {
      await deleteFoodLog(id);
      toast.success('Entry deleted');
    } catch {
      toast.error('Failed to delete entry');
    }
  };

  const getMealLogs = (mealType: MealType): NutritionLog[] => {
    return dailyLogs.filter((log) => log.meal_type === mealType);
  };

  const getMealCalories = (mealType: MealType): number => {
    return getMealLogs(mealType).reduce((sum, log) => sum + log.calories, 0);
  };

  if (isLoading && !dailySummary) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const calorieGoal = goals?.daily_calorie_goal || 2000;
  const totalCalories = dailySummary?.total_calories || 0;
  const caloriePercent = (totalCalories / calorieGoal) * 100;

  return (
    <div className="space-y-6">
      {/* Header with date navigation */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-secondary-900">Nutrition</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleDateChange('prev')}
            className="p-2 hover:bg-secondary-100 rounded-lg"
          >
            <ChevronLeftIcon className="w-5 h-5" />
          </button>
          <span className="px-4 py-2 font-medium text-secondary-900">
            {format(new Date(selectedDate), 'EEE, MMM d')}
          </span>
          <button
            onClick={() => handleDateChange('next')}
            className="p-2 hover:bg-secondary-100 rounded-lg"
            disabled={selectedDate === format(new Date(), 'yyyy-MM-dd')}
          >
            <ChevronRightIcon className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Calorie Summary */}
      <Card>
        <div className="flex flex-col md:flex-row items-center gap-6">
          <ProgressRing
            progress={Math.min(caloriePercent, 100)}
            size={140}
            strokeWidth={10}
            color={caloriePercent > 100 ? '#ef4444' : '#22c55e'}
          >
            <div className="text-center">
              <p className="text-2xl font-bold">{Math.round(totalCalories)}</p>
              <p className="text-xs text-secondary-500">/ {calorieGoal}</p>
            </div>
          </ProgressRing>
          
          <div className="flex-1 grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-lg font-bold text-blue-600">
                {Math.round(dailySummary?.total_protein_g || 0)}g
              </p>
              <p className="text-sm text-secondary-500">Protein</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-orange-600">
                {Math.round(dailySummary?.total_carbs_g || 0)}g
              </p>
              <p className="text-sm text-secondary-500">Carbs</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-bold text-purple-600">
                {Math.round(dailySummary?.total_fat_g || 0)}g
              </p>
              <p className="text-sm text-secondary-500">Fat</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Meal Sections */}
      {mealTypes.map((meal) => (
        <Card key={meal.key}>
          <CardHeader
            title={`${meal.icon} ${meal.label}`}
            subtitle={`${getMealCalories(meal.key)} kcal`}
            action={
              <Button
                size="sm"
                variant="outline"
                leftIcon={<PlusIcon className="w-4 h-4" />}
                onClick={() => {
                  setSelectedMeal(meal.key);
                  setShowAddModal(true);
                }}
              >
                Add
              </Button>
            }
          />
          
          {getMealLogs(meal.key).length > 0 ? (
            <div className="space-y-2">
              {getMealLogs(meal.key).map((log) => (
                <div
                  key={log.id}
                  className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg"
                >
                  <div className="flex-1">
                    <p className="font-medium text-secondary-900">{log.food_name}</p>
                    <p className="text-sm text-secondary-500">
                      {log.quantity} × {log.serving_size}{log.serving_unit}
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-medium">{Math.round(log.calories)} kcal</p>
                      <p className="text-xs text-secondary-500">
                        P: {Math.round(log.protein_g)}g | C: {Math.round(log.carbohydrates_g)}g | F: {Math.round(log.fat_g)}g
                      </p>
                    </div>
                    <button
                      onClick={() => handleDeleteLog(log.id)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-secondary-400 text-center py-4">
              No {meal.label.toLowerCase()} logged
            </p>
          )}
        </Card>
      ))}

      {/* Add Food Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">
                  Add to {mealTypes.find((m) => m.key === selectedMeal)?.label}
                </h2>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setSearchQuery('');
                    clearSearch();
                  }}
                  className="p-2 hover:bg-secondary-100 rounded-lg"
                >
                  ×
                </button>
              </div>
              <Input
                placeholder="Search for food..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                leftIcon={<MagnifyingGlassIcon className="w-5 h-5" />}
              />
            </div>
            
            <div className="p-4 overflow-y-auto max-h-96">
              {isSearching ? (
                <div className="flex justify-center py-8">
                  <LoadingSpinner />
                </div>
              ) : searchResults.length > 0 ? (
                <div className="space-y-2">
                  {searchResults.map((food) => (
                    <button
                      key={food.id}
                      onClick={() => handleAddFood(food)}
                      className="w-full text-left p-3 hover:bg-secondary-50 rounded-lg border border-secondary-200"
                    >
                      <p className="font-medium text-secondary-900">{food.name}</p>
                      {food.brand && (
                        <p className="text-sm text-secondary-500">{food.brand}</p>
                      )}
                      <p className="text-sm text-secondary-500 mt-1">
                        {food.calories} kcal | {food.serving_size}{food.serving_unit}
                      </p>
                    </button>
                  ))}
                </div>
              ) : searchQuery ? (
                <p className="text-center text-secondary-500 py-8">
                  No foods found for "{searchQuery}"
                </p>
              ) : (
                <p className="text-center text-secondary-500 py-8">
                  Search for a food to add
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NutritionPage;
