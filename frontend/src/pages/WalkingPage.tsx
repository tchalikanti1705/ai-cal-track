import React, { useEffect, useState, useCallback } from 'react';
import { format } from 'date-fns';
import { walkingService } from '@/services';
import { useAuthStore } from '@/stores';
import { Card, CardHeader, Button, Input, ProgressRing, LoadingSpinner } from '@/components/ui';
import { WalkingSession, StepCount } from '@/types';
import {
  PlusIcon,
  PlayIcon,
  StopIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export const WalkingPage: React.FC = () => {
  const { goals, profile } = useAuthStore();
  const [stepCount, setStepCount] = useState<StepCount | null>(null);
  const [sessions, setSessions] = useState<WalkingSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeSession, setActiveSession] = useState<WalkingSession | null>(null);
  const [showAddSteps, setShowAddSteps] = useState(false);
  const [stepsInput, setStepsInput] = useState('');

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const today = format(new Date(), 'yyyy-MM-dd');
      const [steps, dailySessions] = await Promise.all([
        walkingService.getDailySteps(today),
        walkingService.getDailySessions(today),
      ]);
      setStepCount(steps);
      setSessions(dailySessions);
      
      // Check for active session
      const active = dailySessions.find((s) => !s.end_time);
      setActiveSession(active || null);
    } catch (error) {
      console.error('Failed to load walking data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleStartSession = async () => {
    try {
      const today = format(new Date(), 'yyyy-MM-dd');
      const now = new Date().toISOString();
      const session = await walkingService.startSession({
        session_date: today,
        start_time: now,
      });
      setActiveSession(session);
      toast.success('Walking session started!');
    } catch {
      toast.error('Failed to start session');
    }
  };

  const handleEndSession = async () => {
    if (!activeSession) return;
    
    try {
      await walkingService.endSession(activeSession.id, {
        end_time: new Date().toISOString(),
      });
      setActiveSession(null);
      toast.success('Session completed!');
      loadData();
    } catch {
      toast.error('Failed to end session');
    }
  };

  const handleLogSteps = async () => {
    if (!stepsInput) return;
    
    try {
      const today = format(new Date(), 'yyyy-MM-dd');
      await walkingService.logSteps({
        count_date: today,
        total_steps: parseInt(stepsInput),
      });
      toast.success('Steps logged!');
      setShowAddSteps(false);
      setStepsInput('');
      loadData();
    } catch {
      toast.error('Failed to log steps');
    }
  };

  const handleDeleteSession = async (id: number) => {
    if (!confirm('Delete this session?')) return;
    try {
      await walkingService.deleteSession(id);
      toast.success('Session deleted');
      loadData();
    } catch {
      toast.error('Failed to delete');
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const stepGoal = goals?.daily_steps_goal || 10000;
  const totalSteps = stepCount?.total_steps || 0;
  const stepPercent = (totalSteps / stepGoal) * 100;
  const distanceKm = stepCount?.total_distance_meters 
    ? (stepCount.total_distance_meters / 1000).toFixed(2) 
    : walkingService.calculateDistanceFromSteps(totalSteps, profile?.height_cm || 170) / 1000;
  const caloriesBurned = stepCount?.total_calories_burned 
    || walkingService.calculateCaloriesFromSteps(totalSteps, profile?.current_weight_kg || 70);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-secondary-900">👣 Walking & Steps</h1>
      </div>

      {/* Steps Progress */}
      <Card>
        <div className="flex flex-col items-center py-4">
          <ProgressRing
            progress={Math.min(stepPercent, 100)}
            size={200}
            strokeWidth={14}
            color={stepPercent >= 100 ? '#22c55e' : '#8b5cf6'}
          >
            <div className="text-center">
              <p className="text-3xl font-bold text-secondary-900">
                {totalSteps.toLocaleString()}
              </p>
              <p className="text-sm text-secondary-500">
                / {stepGoal.toLocaleString()}
              </p>
            </div>
          </ProgressRing>

          <div className="mt-4 flex gap-8 text-center">
            <div>
              <p className="text-lg font-bold text-secondary-900">{Number(distanceKm).toFixed(2)} km</p>
              <p className="text-sm text-secondary-500">Distance</p>
            </div>
            <div>
              <p className="text-lg font-bold text-secondary-900">{Math.round(Number(caloriesBurned))}</p>
              <p className="text-sm text-secondary-500">Calories</p>
            </div>
            <div>
              <p className="text-lg font-bold text-secondary-900">
                {stepCount?.active_minutes || 0}
              </p>
              <p className="text-sm text-secondary-500">Active min</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 gap-4">
        {activeSession ? (
          <Button
            onClick={handleEndSession}
            variant="danger"
            size="lg"
            className="col-span-2"
            leftIcon={<StopIcon className="w-5 h-5" />}
          >
            End Walking Session
          </Button>
        ) : (
          <>
            <Button
              onClick={handleStartSession}
              size="lg"
              leftIcon={<PlayIcon className="w-5 h-5" />}
            >
              Start Walk
            </Button>
            <Button
              onClick={() => setShowAddSteps(true)}
              variant="outline"
              size="lg"
              leftIcon={<PlusIcon className="w-5 h-5" />}
            >
              Log Steps
            </Button>
          </>
        )}
      </div>

      {/* Active Session */}
      {activeSession && (
        <Card className="border-2 border-primary-500 bg-primary-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-primary-900">🚶 Walking in progress...</p>
              <p className="text-sm text-primary-700">
                Started at {format(new Date(activeSession.start_time), 'h:mm a')}
              </p>
            </div>
            <div className="animate-pulse">
              <span className="text-2xl">👣</span>
            </div>
          </div>
        </Card>
      )}

      {/* Today's Sessions */}
      <Card>
        <CardHeader title="Today's Sessions" subtitle={`${sessions.length} walks`} />
        
        {sessions.length > 0 ? (
          <div className="space-y-3">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between p-4 bg-secondary-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                    👣
                  </div>
                  <div>
                    <p className="font-medium text-secondary-900">
                      {session.title || 'Walking Session'}
                    </p>
                    <p className="text-sm text-secondary-500">
                      {format(new Date(session.start_time), 'h:mm a')}
                      {session.end_time && ` - ${format(new Date(session.end_time), 'h:mm a')}`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-medium">{session.steps.toLocaleString()} steps</p>
                    <p className="text-sm text-secondary-500">{session.duration_minutes} min</p>
                  </div>
                  {!activeSession?.id !== session.id && (
                    <button
                      onClick={() => handleDeleteSession(session.id)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-secondary-400 text-center py-8">
            No walking sessions today. Start moving! 👣
          </p>
        )}
      </Card>

      {/* Add Steps Modal */}
      {showAddSteps && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
            <h2 className="text-lg font-semibold mb-4">Log Steps</h2>
            <Input
              label="Number of steps"
              type="number"
              placeholder="e.g., 5000"
              value={stepsInput}
              onChange={(e) => setStepsInput(e.target.value)}
            />
            <div className="flex gap-3 mt-4">
              <Button
                variant="secondary"
                className="flex-1"
                onClick={() => {
                  setShowAddSteps(false);
                  setStepsInput('');
                }}
              >
                Cancel
              </Button>
              <Button className="flex-1" onClick={handleLogSteps}>
                Log Steps
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WalkingPage;
