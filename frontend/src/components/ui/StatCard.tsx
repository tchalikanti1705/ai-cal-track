import React from 'react';
import { clsx } from 'clsx';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: 'green' | 'blue' | 'orange' | 'purple' | 'red';
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  color = 'green',
  className,
}) => {
  const colorStyles = {
    green: {
      bg: 'bg-primary-50',
      icon: 'bg-primary-100 text-primary-600',
      text: 'text-primary-600',
    },
    blue: {
      bg: 'bg-blue-50',
      icon: 'bg-blue-100 text-blue-600',
      text: 'text-blue-600',
    },
    orange: {
      bg: 'bg-orange-50',
      icon: 'bg-orange-100 text-orange-600',
      text: 'text-orange-600',
    },
    purple: {
      bg: 'bg-purple-50',
      icon: 'bg-purple-100 text-purple-600',
      text: 'text-purple-600',
    },
    red: {
      bg: 'bg-red-50',
      icon: 'bg-red-100 text-red-600',
      text: 'text-red-600',
    },
  };

  return (
    <div
      className={clsx(
        'p-4 rounded-xl border border-secondary-200 bg-white',
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-secondary-500 font-medium">{title}</p>
          <p className="mt-1 text-2xl font-bold text-secondary-900">{value}</p>
          {subtitle && (
            <p className="mt-0.5 text-xs text-secondary-400">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div
            className={clsx(
              'p-2 rounded-lg',
              colorStyles[color].icon
            )}
          >
            {icon}
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-2 flex items-center text-xs">
          <span
            className={clsx(
              'font-medium',
              trend.isPositive ? 'text-green-600' : 'text-red-600'
            )}
          >
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
          </span>
          <span className="ml-1 text-secondary-400">vs last week</span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
