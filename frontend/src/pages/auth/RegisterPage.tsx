import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '@/stores';
import { Button, Input } from '@/components/ui';
import toast from 'react-hot-toast';

interface RegisterForm {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register: registerUser, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterForm>();

  const password = watch('password');

  const onSubmit = async (data: RegisterForm) => {
    try {
      await registerUser(data.email, data.password, data.firstName, data.lastName);
      toast.success('Account created successfully!');
      navigate('/onboarding');
    } catch {
      toast.error('Registration failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4 py-8">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-500 rounded-2xl mb-4">
              <span className="text-3xl">🥗</span>
            </div>
            <h1 className="text-2xl font-bold text-secondary-900">Create Account</h1>
            <p className="text-secondary-500 mt-1">Start your health journey today</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="First Name"
                placeholder="John"
                error={errors.firstName?.message}
                {...register('firstName', {
                  required: 'First name is required',
                })}
              />
              <Input
                label="Last Name"
                placeholder="Doe"
                error={errors.lastName?.message}
                {...register('lastName', {
                  required: 'Last name is required',
                })}
              />
            </div>

            <Input
              label="Email"
              type="email"
              placeholder="you@example.com"
              error={errors.email?.message}
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address',
                },
              })}
            />

            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              error={errors.password?.message}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-secondary-400 hover:text-secondary-600"
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              }
              {...register('password', {
                required: 'Password is required',
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters',
                },
                pattern: {
                  value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                  message: 'Must include uppercase, lowercase, and number',
                },
              })}
            />

            <Input
              label="Confirm Password"
              type="password"
              placeholder="••••••••"
              error={errors.confirmPassword?.message}
              {...register('confirmPassword', {
                required: 'Please confirm your password',
                validate: (value) =>
                  value === password || 'Passwords do not match',
              })}
            />

            {/* Password strength indicator */}
            <div className="space-y-2">
              <p className="text-xs text-secondary-500">Password requirements:</p>
              <ul className="text-xs space-y-1">
                <li className={password?.length >= 8 ? 'text-green-600' : 'text-secondary-400'}>
                  ✓ At least 8 characters
                </li>
                <li className={/[A-Z]/.test(password || '') ? 'text-green-600' : 'text-secondary-400'}>
                  ✓ One uppercase letter
                </li>
                <li className={/[a-z]/.test(password || '') ? 'text-green-600' : 'text-secondary-400'}>
                  ✓ One lowercase letter
                </li>
                <li className={/\d/.test(password || '') ? 'text-green-600' : 'text-secondary-400'}>
                  ✓ One number
                </li>
              </ul>
            </div>

            <div className="flex items-start">
              <input
                type="checkbox"
                required
                className="mt-1 w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
              />
              <span className="ml-2 text-sm text-secondary-600">
                I agree to the{' '}
                <Link to="/terms" className="text-primary-600 hover:underline">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-primary-600 hover:underline">
                  Privacy Policy
                </Link>
              </span>
            </div>

            <Button type="submit" className="w-full" size="lg" isLoading={isLoading}>
              Create Account
            </Button>
          </form>

          {/* Sign in link */}
          <p className="mt-6 text-center text-secondary-600">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
