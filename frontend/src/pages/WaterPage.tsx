import React, { useEffect } from 'react';
import { format, addDays, subDays } from 'date-fns';
import { useWaterStore, useAuthStore } from '@/stores';
import { Card, CardHeader, Button, ProgressRing, LoadingSpinner } from '@/components/ui';
import { waterService } from '@/services';
import { ContainerType, WaterLog } from '@/types';
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export const WaterPage: React.FC = () => {
  const { goals } = useAuthStore();
  const {
    selectedDate,
    setSelectedDate,
    dailyLogs,
    dailySummary,
    isLoading,
    isLogging,
    loadDailyData,
    quickAddWater,
    deleteWaterLog,
  } = useWaterStore();

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

  const handleQuickAdd = async (containerType: ContainerType) => {
    try {
      await quickAddWater(containerType);
      toast.success('Water logged!');
    } catch {
      toast.error('Failed to log water');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteWaterLog(id);
      toast.success('Entry deleted');
    } catch {
      toast.error('Failed to delete entry');
    }
  };

  if (isLoading && !dailySummary) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const waterGoal = goals?.water_goal_ml || 2000;
  const totalWater = dailySummary?.total_ml || 0;
  const waterPercent = (totalWater / waterGoal) * 100;
  const containers = waterService.getContainerPresets();

  const formatTime = (dateString: string) => {
    return format(new Date(dateString), 'h:mm a');
  };

  return (
    <div className="space-y-6">
      {/* Header with date navigation */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-secondary-900">💧 Water Intake</h1>
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

      {/* Progress Ring */}
      <Card>
        <div className="flex flex-col items-center py-4">
          <ProgressRing
            progress={Math.min(waterPercent, 100)}
            size={200}
            strokeWidth={14}
            color={waterPercent >= 100 ? '#22c55e' : '#3b82f6'}
          >
            <div className="text-center">
              <p className="text-3xl font-bold text-secondary-900">
                {(totalWater / 1000).toFixed(1)}L
              </p>
              <p className="text-sm text-secondary-500">
                / {(waterGoal / 1000).toFixed(1)}L
              </p>
            </div>
          </ProgressRing>
          
          <p className="mt-4 text-lg font-medium text-secondary-700">
            {waterPercent >= 100 
              ? '🎉 Goal reached!' 
              : `${Math.round(waterGoal - totalWater)}ml to go`}
          </p>
        </div>
      </Card>

      {/* Quick Add Buttons */}
      <Card>
        <CardHeader title="Quick Add" subtitle="Tap to log water" />
        <div className="grid grid-cols-3 sm:grid-cols-5 gap-3">
          {containers.map((container) => (
            <button
              key={container.type}
              onClick={() => handleQuickAdd(container.type)}
              disabled={isLogging}
              className="flex flex-col items-center p-4 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors disabled:opacity-50"
            >
              <span className="text-2xl mb-1">{container.icon}</span>
              <span className="font-medium text-secondary-900">{container.label}</span>
              <span className="text-sm text-secondary-500">{container.amount_ml}ml</span>
            </button>
          ))}
        </div>
      </Card>

      {/* Today's Log */}
      <Card>
        <CardHeader 
          title="Today's Log" 
          subtitle={`${dailyLogs.length} entries`}
        />
        
        {dailyLogs.length > 0 ? (
          <div className="space-y-2">
            {dailyLogs.map((log: WaterLog) => (
              <div
                key={log.id}
                className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    💧
                  </div>
                  <div>
                    <p className="font-medium text-secondary-900">
                      {log.amount_ml}ml
                    </p>
                    <p className="text-sm text-secondary-500">
                      {formatTime(log.log_time)}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(log.id)}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-secondary-400 text-center py-8">
            No water logged yet. Start hydrating! 💧
          </p>
        )}
      </Card>

      {/* Tips */}
      <Card>
        <CardHeader title="💡 Hydration Tips" />
        <ul className="space-y-2 text-secondary-600">
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Drink a glass of water first thing in the morning</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Keep a water bottle at your desk for easy access</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Drink water before, during, and after exercise</span>
          </li>
          <li className="flex items-start gap-2">
            <span>•</span>
            <span>Set reminders to drink water throughout the day</span>
          </li>
        </ul>
      </Card>
    </div>
  );
};

export default WaterPage;
