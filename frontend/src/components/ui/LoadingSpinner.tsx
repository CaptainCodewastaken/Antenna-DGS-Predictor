import React from 'react';
import './LoadingSpinner.css';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', className = '' }) => {
  return (
    <div 
      className={`spinner-container ${size} ${className}`}
      role="status"
      aria-live="polite"
    >
      <div className="spinner"></div>
      <span className="sr-only">Loading...</span>
    </div>
  );
};
