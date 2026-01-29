import React, { useEffect, useState, useCallback } from 'react';
import { format } from 'date-fns';
import { exerciseService } from '@/services';
import { Card, CardHeader, Button, Input, LoadingSpinner } from '@/components/ui';
import { Exercise, ExerciseLog, ExerciseCategory } from '@/types';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  TrashIcon,
  ClockIcon,
  FireIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const categories: { key: ExerciseCategory; label: string; icon: string }[] = [
  { key: 'cardio', label: 'Cardio', icon: '🏃' },
  { key: 'strength', label: 'Strength', icon: '💪' },
  { key: 'yoga', label: 'Yoga', icon: '🧘' },
  { key: 'walking', label: 'Walking', icon: '🚶' },
  { key: 'running', label: 'Running', icon: '🏃‍♂️' },
  { key: 'cycling', label: 'Cycling', icon: '🚴' },
  { key: 'swimming', label: 'Swimming', icon: '🏊' },
  { key: 'hiit', label: 'HIIT', icon: '⚡' },
];

export const ExercisePage: React.FC = () => {
  const [todayLogs, setTodayLogs] = useState<ExerciseLog[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<ExerciseCategory | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [duration, setDuration] = useState('30');
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const today = format(new Date(), 'yyyy-MM-dd');
      const logs = await exerciseService.getDailyLogs(today);
      setTodayLogs(logs);
    } catch (error) {
      console.error('Failed to load exercise data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const loadExercises = async (category?: ExerciseCategory) => {
    try {
      const data = await exerciseService.getExercises(category);
      setExercises(data);
    } catch (error) {
      console.error('Failed to load exercises:', error);
    }
  };

  const handleCategorySelect = (category: ExerciseCategory) => {
    setSelectedCategory(category);
    loadExercises(category);
    setShowAddModal(true);
  };

  const handleLogExercise = async () => {
    if (!selectedExercise || !duration) return;

    try {
      await exerciseService.logExercise({
        exercise_type_id: selectedExercise.id,
        log_date: format(new Date(), 'yyyy-MM-dd'),
        duration_minutes: parseInt(duration),
        exercise_name: selectedExercise.name,
        category: selectedExercise.category,
        intensity: 'moderate',
      });
      
      toast.success('Exercise logged!');
      setShowAddModal(false);
      setSelectedExercise(null);
      setDuration('30');
      loadData();
    } catch {
      toast.error('Failed to log exercise');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this exercise?')) return;
    try {
      await exerciseService.deleteExerciseLog(id);
      toast.success('Exercise deleted');
      loadData();
    } catch {
      toast.error('Failed to delete');
    }
  };

  const totalMinutes = todayLogs.reduce((sum, log) => sum + log.duration_minutes, 0);
  const totalCalories = todayLogs.reduce((sum, log) => sum + log.calories_burned, 0);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-secondary-900">🏋️ Exercise</h1>
      </div>

      {/* Today's Summary */}
      <div className="grid grid-cols-2 gap-4">
        <Card className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <ClockIcon className="w-5 h-5 text-blue-500" />
            <span className="text-sm text-secondary-500">Duration</span>
          </div>
          <p className="text-3xl font-bold text-secondary-900">{totalMinutes}</p>
          <p className="text-secondary-500">minutes</p>
        </Card>
        <Card className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <FireIcon className="w-5 h-5 text-orange-500" />
            <span className="text-sm text-secondary-500">Burned</span>
          </div>
          <p className="text-3xl font-bold text-secondary-900">{Math.round(totalCalories)}</p>
          <p className="text-secondary-500">kcal</p>
        </Card>
      </div>

      {/* Quick Add by Category */}
      <Card>
        <CardHeader title="Log Exercise" subtitle="Select a category" />
        <div className="grid grid-cols-4 gap-3">
          {categories.map((cat) => (
            <button
              key={cat.key}
              onClick={() => handleCategorySelect(cat.key)}
              className="flex flex-col items-center p-3 bg-secondary-50 hover:bg-secondary-100 rounded-xl transition-colors"
            >
              <span className="text-2xl mb-1">{cat.icon}</span>
              <span className="text-xs font-medium text-secondary-700">{cat.label}</span>
            </button>
          ))}
        </div>
      </Card>

      {/* Today's Exercises */}
      <Card>
        <CardHeader title="Today's Workouts" subtitle={`${todayLogs.length} sessions`} />
        
        {todayLogs.length > 0 ? (
          <div className="space-y-3">
            {todayLogs.map((log) => (
              <div
                key={log.id}
                className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-xl">
                    {categories.find((c) => c.key === log.category)?.icon || '🏃'}
                  </div>
                  <div>
                    <p className="font-medium text-secondary-900">{log.exercise_name}</p>
                    <p className="text-sm text-secondary-500">
                      {log.duration_minutes} min • {log.intensity}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-medium text-orange-600">
                      {Math.round(log.calories_burned)} kcal
                    </p>
                  </div>
                  <button
                    onClick={() => handleDelete(log.id)}
                    className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-secondary-400 mb-4">No exercise logged today</p>
            <Button
              onClick={() => handleCategorySelect('cardio')}
              leftIcon={<PlusIcon className="w-4 h-4" />}
            >
              Log your first workout
            </Button>
          </div>
        )}
      </Card>

      {/* Add Exercise Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[80vh] overflow-hidden">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">
                  {categories.find((c) => c.key === selectedCategory)?.icon}{' '}
                  Add {categories.find((c) => c.key === selectedCategory)?.label}
                </h2>
                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setSelectedExercise(null);
                  }}
                  className="p-2 hover:bg-secondary-100 rounded-lg"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-4 overflow-y-auto max-h-80">
              {exercises.length > 0 ? (
                <div className="space-y-2">
                  {exercises.map((exercise) => (
                    <button
                      key={exercise.id}
                      onClick={() => setSelectedExercise(exercise)}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        selectedExercise?.id === exercise.id
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-secondary-200 hover:bg-secondary-50'
                      }`}
                    >
                      <p className="font-medium text-secondary-900">{exercise.name}</p>
                      {exercise.description && (
                        <p className="text-sm text-secondary-500">{exercise.description}</p>
                      )}
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-center text-secondary-500 py-4">Loading exercises...</p>
              )}
            </div>

            {selectedExercise && (
              <div className="p-4 border-t bg-secondary-50">
                <div className="flex items-center gap-4">
                  <Input
                    label="Duration (minutes)"
                    type="number"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    className="w-32"
                  />
                  <Button onClick={handleLogExercise} className="flex-1">
                    Log Exercise
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ExercisePage;

