import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PredictionCards } from '../components/Predictions/PredictionCards';

vi.mock('../components/ui/AnimatedNumber', () => ({
  AnimatedNumber: ({ value, format }: any) => <span>{format(value)}</span>
}));

describe('PredictionCards', () => {
  it('renders loading state correctly', () => {
    const { container } = render(<PredictionCards data={null} loading={true} />);
    expect(container.querySelector('.prediction-overlay')).toBeInTheDocument();
  });

  it('renders predictions correctly and handles ML overrides', () => {
    const mockData = {
      physics_baseline: {
        resonant_frequency_hz: 2.4e9,
        bandwidth_hz: 80e6,
        gain_dbi: 5.0,
        radiation_efficiency: 0.5,
        directivity_dbi: 8.0,
        input_impedance_ohms: 50.0,
        quality_factor: 33.3
      },
      ml_predictions: {
        xgboost: {
          resonant_frequency_hz: 2.45e9, // Overrides
          gain_dbi: 5.5, // Overrides
          // Notice bandwidth_hz and radiation_efficiency are not here in ML
        }
      }
    };

    render(<PredictionCards data={mockData as any} loading={false} selectedModel="xgboost" />);
    
    // Check if ML predictions show
    expect(screen.getByText('2.450')).toBeInTheDocument(); // ML frequency
    expect(screen.getByText('5.50')).toBeInTheDocument(); // ML gain
    // Check if baselines show as fallback
    expect(screen.getByText('80.0')).toBeInTheDocument(); // Baseline bandwidth
    expect(screen.getByText('50.0')).toBeInTheDocument(); // Baseline efficiency
  });
});
