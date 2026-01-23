import React, { useEffect, useState, useCallback } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { format, subDays } from 'date-fns';
import { insightsService } from '@/services';
import { Card, CardHeader, LoadingSpinner } from '@/components/ui';
import { WeeklyTrend } from '@/types';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export const InsightsPage: React.FC = () => {
  const [weeklyTrends, setWeeklyTrends] = useState<WeeklyTrend | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const trends = await insightsService.getWeeklyTrends();
      setWeeklyTrends(trends);
    } catch (error) {
      console.error('Failed to load insights:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (isLoading || !weeklyTrends) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Generate day labels
  const dayLabels = Array.from({ length: 7 }, (_, i) => 
    format(subDays(new Date(), 6 - i), 'EEE')
  );

  // Calories Line Chart
  const caloriesData = {
    labels: dayLabels,
    datasets: [
      {
        label: 'Calories',
        data: weeklyTrends.calories.daily,
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Water Bar Chart
  const waterData = {
    labels: dayLabels,
    datasets: [
      {
        label: 'Water (ml)',
        data: weeklyTrends.water.daily,
        backgroundColor: '#3b82f6',
        borderRadius: 4,
      },
    ],
  };

  // Steps Bar Chart
  const stepsData = {
    labels: dayLabels,
    datasets: [
      {
        label: 'Steps',
        data: weeklyTrends.steps.daily,
        backgroundColor: '#8b5cf6',
        borderRadius: 4,
      },
    ],
  };

  // Exercise Bar Chart
  const exerciseData = {
    labels: dayLabels,
    datasets: [
      {
        label: 'Exercise (min)',
        data: weeklyTrends.exercise.daily_minutes,
        backgroundColor: '#f97316',
        borderRadius: 4,
      },
    ],
  };

  // Macro Doughnut
  const macroData = {
    labels: ['Protein', 'Carbs', 'Fat'],
    datasets: [
      {
        data: [30, 45, 25], // Example percentages
        backgroundColor: ['#3b82f6', '#f97316', '#8b5cf6'],
        borderWidth: 0,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: '#f1f5f9',
        },
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
    cutout: '70%',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-secondary-900">📊 Insights</h1>
        <p className="text-secondary-500">
          Your health trends for the past 7 days
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="text-center">
          <p className="text-sm text-secondary-500">Avg Calories</p>
          <p className="text-2xl font-bold text-secondary-900">
            {weeklyTrends.calories.average}
          </p>
          <p className="text-xs text-green-600">
            {weeklyTrends.calories.goal_met_days}/7 days on target
          </p>
        </Card>
        <Card className="text-center">
          <p className="text-sm text-secondary-500">Avg Water</p>
          <p className="text-2xl font-bold text-secondary-900">
            {(weeklyTrends.water.average / 1000).toFixed(1)}L
          </p>
          <p className="text-xs text-blue-600">
            {weeklyTrends.water.goal_met_days}/7 days on target
          </p>
        </Card>
        <Card className="text-center">
          <p className="text-sm text-secondary-500">Avg Steps</p>
          <p className="text-2xl font-bold text-secondary-900">
            {weeklyTrends.steps.average.toLocaleString()}
          </p>
          <p className="text-xs text-purple-600">
            {weeklyTrends.steps.goal_met_days}/7 days on target
          </p>
        </Card>
        <Card className="text-center">
          <p className="text-sm text-secondary-500">Total Exercise</p>
          <p className="text-2xl font-bold text-secondary-900">
            {weeklyTrends.exercise.total_minutes} min
          </p>
          <p className="text-xs text-orange-600">
            {weeklyTrends.exercise.sessions} sessions
          </p>
        </Card>
      </div>

      {/* Calories Chart */}
      <Card>
        <CardHeader title="Calorie Intake" subtitle="Daily calories consumed" />
        <div className="h-64">
          <Line data={caloriesData} options={chartOptions} />
        </div>
      </Card>

      {/* Water & Steps Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Water Intake" subtitle="Daily hydration (ml)" />
          <div className="h-48">
            <Bar data={waterData} options={chartOptions} />
          </div>
        </Card>
        <Card>
          <CardHeader title="Daily Steps" subtitle="Step count per day" />
          <div className="h-48">
            <Bar data={stepsData} options={chartOptions} />
          </div>
        </Card>
      </div>

      {/* Exercise & Macros */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Exercise" subtitle="Minutes per day" />
          <div className="h-48">
            <Bar data={exerciseData} options={chartOptions} />
          </div>
        </Card>
        <Card>
          <CardHeader title="Macro Distribution" subtitle="Average breakdown" />
          <div className="h-48">
            <Doughnut data={macroData} options={doughnutOptions} />
          </div>
        </Card>
      </div>

      {/* Weight Progress */}
      {weeklyTrends.weight.start_kg && weeklyTrends.weight.end_kg && (
        <Card>
          <CardHeader title="Weight Progress" />
          <div className="flex items-center justify-center gap-8 py-4">
            <div className="text-center">
              <p className="text-sm text-secondary-500">Start of Week</p>
              <p className="text-2xl font-bold">{weeklyTrends.weight.start_kg} kg</p>
            </div>
            <div className="text-4xl">→</div>
            <div className="text-center">
              <p className="text-sm text-secondary-500">End of Week</p>
              <p className="text-2xl font-bold">{weeklyTrends.weight.end_kg} kg</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-secondary-500">Change</p>
              <p className={`text-2xl font-bold ${
                (weeklyTrends.weight.change_kg || 0) < 0 
                  ? 'text-green-600' 
                  : 'text-red-600'
              }`}>
                {weeklyTrends.weight.change_kg && weeklyTrends.weight.change_kg > 0 ? '+' : ''}
                {weeklyTrends.weight.change_kg} kg
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Tips */}
      <Card>
        <CardHeader title="💡 Weekly Insights" />
        <ul className="space-y-3 text-secondary-600">
          <li className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
            <span className="text-xl">✅</span>
            <span>
              You met your calorie goal {weeklyTrends.calories.goal_met_days} days this week. 
              {weeklyTrends.calories.goal_met_days >= 5 ? ' Great consistency!' : ' Keep working at it!'}
            </span>
          </li>
          <li className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
            <span className="text-xl">💧</span>
            <span>
              Average water intake: {(weeklyTrends.water.average / 1000).toFixed(1)}L daily.
              {weeklyTrends.water.average >= 2000 ? ' Excellent hydration!' : ' Try to drink more water.'}
            </span>
          </li>
          <li className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
            <span className="text-xl">👣</span>
            <span>
              Average steps: {weeklyTrends.steps.average.toLocaleString()} per day.
              {weeklyTrends.steps.average >= 10000 ? ' You\'re crushing it!' : ' Try to add more movement.'}
            </span>
          </li>
          <li className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg">
            <span className="text-xl">🏋️</span>
            <span>
              Total exercise: {weeklyTrends.exercise.total_minutes} minutes across {weeklyTrends.exercise.sessions} sessions.
              {weeklyTrends.exercise.total_minutes >= 150 ? ' Meeting WHO recommendations!' : ' Aim for 150+ min/week.'}
            </span>
          </li>
        </ul>
      </Card>
    </div>
  );
};

export default InsightsPage;
