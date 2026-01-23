import React from 'react';
import { clsx } from 'clsx';

interface ProgressRingProps {
  progress: number; // 0-100
  size?: number;
  strokeWidth?: number;
  color?: string;
  bgColor?: string;
  children?: React.ReactNode;
  className?: string;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  progress,
  size = 120,
  strokeWidth = 8,
  color = '#22c55e',
  bgColor = '#e2e8f0',
  children,
  className,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const progressValue = Math.min(Math.max(progress, 0), 100);
  const strokeDashoffset = circumference - (progressValue / 100) * circumference;

  return (
    <div className={clsx('relative inline-flex items-center justify-center', className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={bgColor}
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
      </svg>
      {children && (
        <div className="absolute inset-0 flex items-center justify-center">
          {children}
        </div>
      )}
    </div>
  );
};

interface ProgressBarProps {
  progress: number;
  height?: number;
  color?: string;
  bgColor?: string;
  showLabel?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  height = 8,
  color = 'bg-primary-500',
  bgColor = 'bg-secondary-200',
  showLabel = false,
  className,
}) => {
  const progressValue = Math.min(Math.max(progress, 0), 100);

  return (
    <div className={className}>
      <div
        className={clsx('w-full rounded-full overflow-hidden', bgColor)}
        style={{ height }}
      >
        <div
          className={clsx('h-full rounded-full transition-all duration-500 ease-out', color)}
          style={{ width: `${progressValue}%` }}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between mt-1 text-xs text-secondary-500">
          <span>{Math.round(progressValue)}%</span>
        </div>
      )}
    </div>
  );
};

export default ProgressRing;
