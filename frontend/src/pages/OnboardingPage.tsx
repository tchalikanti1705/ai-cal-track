import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '@/stores';
import { userService } from '@/services';
import { Button, Input, Card } from '@/components/ui';
import toast from 'react-hot-toast';
import {
  UserIcon,
  CalendarIcon,
  ScaleIcon,
  FireIcon,
  FlagIcon,
} from '@heroicons/react/24/outline';

interface OnboardingData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: 'male' | 'female' | 'other';
  height_cm: number;
  weight_kg: number;
  target_weight_kg: number;
  activity_level: 'sedentary' | 'lightly_active' | 'moderately_active' | 'very_active' | 'extra_active';
  goal_type: 'lose_weight' | 'maintain_weight' | 'gain_weight';
  weekly_goal_kg: number;
}

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Sedentary', description: 'Little or no exercise' },
  { value: 'lightly_active', label: 'Lightly Active', description: '1-3 days/week' },
  { value: 'moderately_active', label: 'Moderately Active', description: '3-5 days/week' },
  { value: 'very_active', label: 'Very Active', description: '6-7 days/week' },
  { value: 'extra_active', label: 'Extra Active', description: 'Intense daily exercise' },
];

const GOAL_TYPES = [
  { value: 'lose_weight', label: 'Lose Weight', icon: '📉' },
  { value: 'maintain_weight', label: 'Maintain Weight', icon: '⚖️' },
  { value: 'gain_weight', label: 'Gain Weight', icon: '📈' },
];

export const OnboardingPage: React.FC = () => {
  const navigate = useNavigate();
  const { loadUser } = useAuthStore();
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<OnboardingData>({
    defaultValues: {
      gender: 'male',
      activity_level: 'moderately_active',
      goal_type: 'maintain_weight',
      weekly_goal_kg: 0.5,
    }
  });

  const formData = watch();
  const totalSteps = 5;

  const calculateBMI = () => {
    if (formData.height_cm && formData.weight_kg) {
      const heightM = formData.height_cm / 100;
      const bmi = formData.weight_kg / (heightM * heightM);
      return bmi.toFixed(1);
    }
    return null;
  };

  const getBMICategory = (bmi: number) => {
    if (bmi < 18.5) return { label: 'Underweight', color: 'text-blue-600' };
    if (bmi < 25) return { label: 'Normal', color: 'text-green-600' };
    if (bmi < 30) return { label: 'Overweight', color: 'text-orange-600' };
    return { label: 'Obese', color: 'text-red-600' };
  };

  const calculateDailyCalories = () => {
    if (!formData.weight_kg || !formData.height_cm || !formData.date_of_birth || !formData.gender) {
      return null;
    }

    // Calculate age
    const today = new Date();
    const birthDate = new Date(formData.date_of_birth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }

    // Mifflin-St Jeor Equation
    let bmr: number;
    if (formData.gender === 'male') {
      bmr = 10 * formData.weight_kg + 6.25 * formData.height_cm - 5 * age + 5;
    } else {
      bmr = 10 * formData.weight_kg + 6.25 * formData.height_cm - 5 * age - 161;
    }

    // Activity multiplier
    const activityMultipliers: Record<string, number> = {
      sedentary: 1.2,
      lightly_active: 1.375,
      moderately_active: 1.55,
      very_active: 1.725,
      extra_active: 1.9,
    };

    const tdee = bmr * (activityMultipliers[formData.activity_level] || 1.55);

    // Adjust for goal
    let calories = tdee;
    if (formData.goal_type === 'lose_weight') {
      calories = tdee - (formData.weekly_goal_kg * 1100); // ~1100 cal deficit per kg/week
    } else if (formData.goal_type === 'gain_weight') {
      calories = tdee + (formData.weekly_goal_kg * 1100);
    }

    return Math.round(Math.max(1200, calories)); // Minimum 1200 calories
  };

  const onSubmit = async (data: OnboardingData) => {
    setIsSubmitting(true);
    try {
      // Convert string values to numbers
      const heightCm = Number(data.height_cm);
      const weightKg = Number(data.weight_kg);
      const targetWeightKg = Number(data.target_weight_kg);

      // Update profile
      await userService.updateProfile({
        first_name: data.first_name,
        last_name: data.last_name,
        date_of_birth: data.date_of_birth,
        gender: data.gender,
        height_cm: heightCm,
        current_weight_kg: weightKg,
        activity_level: data.activity_level,
      });

      // Calculate daily goals
      const dailyCalories = calculateDailyCalories() || 2000;
      const proteinGoal = Math.round(weightKg * 1.6); // 1.6g per kg
      const fatGoal = Math.round((dailyCalories * 0.25) / 9); // 25% of calories
      const carbsGoal = Math.round((dailyCalories - (proteinGoal * 4) - (fatGoal * 9)) / 4);

      // Update goals
      await userService.updateGoals({
        daily_calorie_goal: dailyCalories,
        weight_goal_kg: targetWeightKg,
        goal_type: data.goal_type,
        weight_change_rate: data.weekly_goal_kg,
        protein_goal_g: proteinGoal,
        carbs_goal_g: carbsGoal,
        fat_goal_g: fatGoal,
        water_goal_ml: 2500,
        daily_steps_goal: 10000,
      });

      // Reload user to get updated profile
      await loadUser();

      toast.success('Profile setup complete!');
      navigate('/dashboard');
    } catch (error) {
      console.error('Onboarding error:', error);
      toast.error('Failed to save profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => setStep((prev) => Math.min(prev + 1, totalSteps));
  const prevStep = () => setStep((prev) => Math.max(prev - 1, 1));

  const renderProgressBar = () => (
    <div className="mb-8">
      <div className="flex gap-2 mb-2">
        {Array.from({ length: totalSteps }).map((_, index) => (
          <div
            key={index}
            className={`h-2 flex-1 rounded-full transition-colors ${
              index < step ? 'bg-primary-500' : 'bg-secondary-200'
            }`}
          />
        ))}
      </div>
      <p className="text-sm text-secondary-500">Step {step} of {totalSteps}</p>
    </div>
  );

  const renderStep1 = () => (
    <div className="text-center">
      <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
        <UserIcon className="w-8 h-8 text-primary-600" />
      </div>
      <h2 className="text-2xl font-bold text-secondary-900 mb-2">What's your name?</h2>
      <p className="text-secondary-500 mb-8">Let's personalize your experience</p>

      <div className="space-y-4 text-left">
        <Input
          label="First Name"
          placeholder="Enter your first name"
          error={errors.first_name?.message}
          {...register('first_name', { required: 'First name is required' })}
        />
        <Input
          label="Last Name"
          placeholder="Enter your last name"
          error={errors.last_name?.message}
          {...register('last_name', { required: 'Last name is required' })}
        />
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="text-center">
      <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
        <CalendarIcon className="w-8 h-8 text-primary-600" />
      </div>
      <h2 className="text-2xl font-bold text-secondary-900 mb-2">Tell us about yourself</h2>
      <p className="text-secondary-500 mb-8">This helps us calculate your goals</p>

      <div className="space-y-6 text-left">
        <Input
          label="Date of Birth"
          type="date"
          error={errors.date_of_birth?.message}
          {...register('date_of_birth', { required: 'Date of birth is required' })}
        />

        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">Gender</label>
          <div className="grid grid-cols-3 gap-3">
            {['male', 'female', 'other'].map((gender) => (
              <button
                key={gender}
                type="button"
                onClick={() => setValue('gender', gender as 'male' | 'female' | 'other')}
                className={`p-3 rounded-xl border-2 transition-all ${
                  formData.gender === gender
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-secondary-200 hover:border-secondary-300'
                }`}
              >
                <span className="capitalize font-medium">{gender}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => {
    const bmi = calculateBMI();
    const bmiCategory = bmi ? getBMICategory(parseFloat(bmi)) : null;

    return (
      <div className="text-center">
        <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <ScaleIcon className="w-8 h-8 text-primary-600" />
        </div>
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">Your measurements</h2>
        <p className="text-secondary-500 mb-8">We'll calculate your BMI and calorie needs</p>

        <div className="space-y-4 text-left">
          <Input
            label="Height (cm)"
            type="number"
            placeholder="170"
            error={errors.height_cm?.message}
            {...register('height_cm', { 
              required: 'Height is required',
              min: { value: 100, message: 'Height must be at least 100 cm' },
              max: { value: 250, message: 'Height must be less than 250 cm' }
            })}
          />
          <Input
            label="Current Weight (kg)"
            type="number"
            step="0.1"
            placeholder="70"
            error={errors.weight_kg?.message}
            {...register('weight_kg', { 
              required: 'Weight is required',
              min: { value: 30, message: 'Weight must be at least 30 kg' },
              max: { value: 300, message: 'Weight must be less than 300 kg' }
            })}
          />
        </div>

        {bmi && (
          <div className="mt-6 p-4 bg-secondary-50 rounded-xl">
            <p className="text-sm text-secondary-500 mb-1">Your BMI</p>
            <p className="text-3xl font-bold text-secondary-900">{bmi}</p>
            <p className={`text-sm font-medium ${bmiCategory?.color}`}>{bmiCategory?.label}</p>
          </div>
        )}
      </div>
    );
  };

  const renderStep4 = () => (
    <div className="text-center">
      <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
        <FireIcon className="w-8 h-8 text-primary-600" />
      </div>
      <h2 className="text-2xl font-bold text-secondary-900 mb-2">How active are you?</h2>
      <p className="text-secondary-500 mb-8">This helps us estimate your calorie needs</p>

      <div className="space-y-3">
        {ACTIVITY_LEVELS.map((level) => (
          <button
            key={level.value}
            type="button"
            onClick={() => setValue('activity_level', level.value as OnboardingData['activity_level'])}
            className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
              formData.activity_level === level.value
                ? 'border-primary-500 bg-primary-50'
                : 'border-secondary-200 hover:border-secondary-300'
            }`}
          >
            <p className="font-medium text-secondary-900">{level.label}</p>
            <p className="text-sm text-secondary-500">{level.description}</p>
          </button>
        ))}
      </div>
    </div>
  );

  const renderStep5 = () => {
    const dailyCalories = calculateDailyCalories();

    return (
      <div className="text-center">
        <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <FlagIcon className="w-8 h-8 text-primary-600" />
        </div>
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">Set your goal</h2>
        <p className="text-secondary-500 mb-8">What do you want to achieve?</p>

        <div className="space-y-6 text-left">
          <div className="grid grid-cols-3 gap-3">
            {GOAL_TYPES.map((goal) => (
              <button
                key={goal.value}
                type="button"
                onClick={() => setValue('goal_type', goal.value as OnboardingData['goal_type'])}
                className={`p-4 rounded-xl border-2 text-center transition-all ${
                  formData.goal_type === goal.value
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-secondary-200 hover:border-secondary-300'
                }`}
              >
                <span className="text-2xl mb-2 block">{goal.icon}</span>
                <span className="text-sm font-medium">{goal.label}</span>
              </button>
            ))}
          </div>

          <Input
            label="Target Weight (kg)"
            type="number"
            step="0.1"
            placeholder="65"
            error={errors.target_weight_kg?.message}
            {...register('target_weight_kg', { 
              required: 'Target weight is required',
              min: { value: 30, message: 'Weight must be at least 30 kg' },
              max: { value: 300, message: 'Weight must be less than 300 kg' }
            })}
          />

          {formData.goal_type !== 'maintain_weight' && (
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Weekly goal
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[0.25, 0.5, 1].map((rate) => (
                  <button
                    key={rate}
                    type="button"
                    onClick={() => setValue('weekly_goal_kg', rate)}
                    className={`p-3 rounded-xl border-2 transition-all ${
                      formData.weekly_goal_kg === rate
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-secondary-200 hover:border-secondary-300'
                    }`}
                  >
                    <p className="font-medium text-secondary-900">{rate} kg</p>
                    <p className="text-xs text-secondary-500">per week</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {dailyCalories && (
            <div className="p-4 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl text-white">
              <p className="text-sm opacity-90 mb-1">Your recommended daily calories</p>
              <p className="text-3xl font-bold">{dailyCalories} kcal</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return formData.first_name && formData.last_name;
      case 2:
        return formData.date_of_birth && formData.gender;
      case 3:
        return formData.height_cm && formData.weight_kg;
      case 4:
        return formData.activity_level;
      case 5:
        return formData.goal_type && formData.target_weight_kg;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg p-8">
        {renderProgressBar()}

        <form onSubmit={handleSubmit(onSubmit)}>
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
          {step === 4 && renderStep4()}
          {step === 5 && renderStep5()}

          <div className="flex gap-4 mt-8">
            {step > 1 && (
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={prevStep}
              >
                ← Back
              </Button>
            )}
            {step < totalSteps ? (
              <Button
                type="button"
                className="flex-1"
                onClick={nextStep}
                disabled={!canProceed()}
              >
                Continue →
              </Button>
            ) : (
              <Button
                type="submit"
                className="flex-1"
                isLoading={isSubmitting}
                disabled={!canProceed()}
              >
                Complete Setup 🎉
              </Button>
            )}
          </div>
        </form>
      </Card>
    </div>
  );
};

export default OnboardingPage;

