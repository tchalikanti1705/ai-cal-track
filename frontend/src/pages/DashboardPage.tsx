import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { useAuthStore, useDashboardStore } from '@/stores';
import { Card, CardHeader, ProgressRing, ProgressBar, StatCard, LoadingSpinner } from '@/components/ui';
import {
  FireIcon,
  BeakerIcon,
  HeartIcon,
  CameraIcon,
} from '@heroicons/react/24/outline';

export const DashboardPage: React.FC = () => {
  const { profile } = useAuthStore();
  const { dashboard, isLoading, loadDashboard, loadRecommendations, recommendations } = useDashboardStore();

  useEffect(() => {
    loadDashboard();
    loadRecommendations();
  }, [loadDashboard, loadRecommendations]);

  if (isLoading || !dashboard) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const caloriePercent = dashboard.nutrition.calories.percent;
  const calorieColor = caloriePercent > 100 ? '#ef4444' : caloriePercent > 80 ? '#f97316' : '#22c55e';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">
            {greeting()}, {profile?.first_name || 'there'}! 👋
          </h1>
          <p className="text-secondary-500">{format(new Date(), 'EEEE, MMMM d, yyyy')}</p>
        </div>
        <Link
          to="/scan"
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <CameraIcon className="w-5 h-5" />
          <span className="hidden sm:inline">Scan Food</span>
        </Link>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calories Ring */}
        <Card className="lg:col-span-1">
          <CardHeader title="Today's Calories" subtitle="Daily goal progress" />
          <div className="flex flex-col items-center">
            <ProgressRing
              progress={Math.min(caloriePercent, 100)}
              size={180}
              strokeWidth={12}
              color={calorieColor}
            >
              <div className="text-center">
                <p className="text-3xl font-bold text-secondary-900">
                  {dashboard.nutrition.calories.consumed}
                </p>
                <p className="text-sm text-secondary-500">
                  / {dashboard.nutrition.calories.goal} kcal
                </p>
              </div>
            </ProgressRing>
            <div className="mt-4 text-center">
              <p className="text-lg font-semibold text-secondary-900">
                {dashboard.nutrition.calories.remaining > 0
                  ? `${dashboard.nutrition.calories.remaining} kcal remaining`
                  : `${Math.abs(dashboard.nutrition.calories.goal - dashboard.nutrition.calories.consumed)} kcal over`}
              </p>
            </div>
          </div>
        </Card>

        {/* Macros */}
        <Card className="lg:col-span-2">
          <CardHeader title="Macronutrients" subtitle="Daily breakdown" />
          <div className="space-y-4">
            {/* Protein */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-secondary-700">Protein</span>
                <span className="text-sm text-secondary-500">
                  {dashboard.nutrition.protein.consumed}g / {dashboard.nutrition.protein.goal}g
                </span>
              </div>
              <ProgressBar
                progress={dashboard.nutrition.protein.percent}
                color="bg-blue-500"
              />
            </div>

            {/* Carbs */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-secondary-700">Carbohydrates</span>
                <span className="text-sm text-secondary-500">
                  {dashboard.nutrition.carbs.consumed}g / {dashboard.nutrition.carbs.goal}g
                </span>
              </div>
              <ProgressBar
                progress={dashboard.nutrition.carbs.percent}
                color="bg-orange-500"
              />
            </div>

            {/* Fat */}
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-secondary-700">Fat</span>
                <span className="text-sm text-secondary-500">
                  {dashboard.nutrition.fat.consumed}g / {dashboard.nutrition.fat.goal}g
                </span>
              </div>
              <ProgressBar
                progress={dashboard.nutrition.fat.percent}
                color="bg-purple-500"
              />
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Water"
          value={`${(dashboard.water.consumed / 1000).toFixed(1)}L`}
          subtitle={`Goal: ${(dashboard.water.goal / 1000).toFixed(1)}L`}
          icon={<BeakerIcon className="w-5 h-5" />}
          color="blue"
        />
        <StatCard
          title="Steps"
          value={dashboard.steps.count.toLocaleString()}
          subtitle={`Goal: ${dashboard.steps.goal.toLocaleString()}`}
          icon={<HeartIcon className="w-5 h-5" />}
          color="green"
        />
        <StatCard
          title="Exercise"
          value={`${dashboard.exercise.minutes} min`}
          subtitle={`${dashboard.exercise.calories_burned} kcal burned`}
          icon={<HeartIcon className="w-5 h-5" />}
          color="orange"
        />
        <StatCard
          title="Net Calories"
          value={`${dashboard.net_calories}`}
          subtitle="Consumed - Burned"
          icon={<FireIcon className="w-5 h-5" />}
          color="purple"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          to="/nutrition"
          className="flex flex-col items-center p-4 bg-white rounded-xl border border-secondary-200 hover:border-primary-300 hover:shadow-md transition-all"
        >
          <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mb-3">
            <FireIcon className="w-6 h-6 text-orange-600" />
          </div>
          <span className="font-medium text-secondary-900">Log Food</span>
        </Link>
        <Link
          to="/water"
          className="flex flex-col items-center p-4 bg-white rounded-xl border border-secondary-200 hover:border-primary-300 hover:shadow-md transition-all"
        >
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
            <BeakerIcon className="w-6 h-6 text-blue-600" />
          </div>
          <span className="font-medium text-secondary-900">Log Water</span>
        </Link>
        <Link
          to="/exercise"
          className="flex flex-col items-center p-4 bg-white rounded-xl border border-secondary-200 hover:border-primary-300 hover:shadow-md transition-all"
        >
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
            <HeartIcon className="w-6 h-6 text-green-600" />
          </div>
          <span className="font-medium text-secondary-900">Log Exercise</span>
        </Link>
        <Link
          to="/scan"
          className="flex flex-col items-center p-4 bg-white rounded-xl border border-secondary-200 hover:border-primary-300 hover:shadow-md transition-all"
        >
          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-3">
            <CameraIcon className="w-6 h-6 text-purple-600" />
          </div>
          <span className="font-medium text-secondary-900">Scan Food</span>
        </Link>
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <Card>
          <CardHeader title="Recommendations" subtitle="Personalized tips for you" />
          <div className="space-y-3">
            {recommendations.slice(0, 3).map((rec) => (
              <div
                key={rec.id}
                className="flex items-start gap-3 p-3 bg-secondary-50 rounded-lg"
              >
                <div
                  className={`w-2 h-2 mt-2 rounded-full ${
                    rec.priority === 'high'
                      ? 'bg-red-500'
                      : rec.priority === 'medium'
                      ? 'bg-orange-500'
                      : 'bg-green-500'
                  }`}
                />
                <div>
                  <p className="font-medium text-secondary-900">{rec.title}</p>
                  <p className="text-sm text-secondary-500">{rec.message}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default DashboardPage;
