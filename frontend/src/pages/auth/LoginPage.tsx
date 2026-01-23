import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '@/stores';
import { Button, Input } from '@/components/ui';
import toast from 'react-hot-toast';

interface LoginForm {
  email: string;
  password: string;
}

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>();

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard';

  const onSubmit = async (data: LoginForm) => {
    try {
      await login(data.email, data.password);
      toast.success('Welcome back!');
      navigate(from, { replace: true });
    } catch {
      toast.error('Invalid email or password');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-500 rounded-2xl mb-4">
              <span className="text-3xl">🥗</span>
            </div>
            <h1 className="text-2xl font-bold text-secondary-900">Welcome Back</h1>
            <p className="text-secondary-500 mt-1">Sign in to continue tracking</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
                  value: 6,
                  message: 'Password must be at least 6 characters',
                },
              })}
            />

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
                />
                <span className="ml-2 text-secondary-600">Remember me</span>
              </label>
              <Link
                to="/forgot-password"
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Forgot password?
              </Link>
            </div>

            <Button type="submit" className="w-full" size="lg" isLoading={isLoading}>
              Sign in
            </Button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center">
            <div className="flex-1 border-t border-secondary-200" />
            <span className="px-4 text-sm text-secondary-400">or</span>
            <div className="flex-1 border-t border-secondary-200" />
          </div>

          {/* Sign up link */}
          <p className="text-center text-secondary-600">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Sign up free
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
