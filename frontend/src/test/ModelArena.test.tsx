
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ModelArena } from '../components/ModelComparison/ModelArena';
import * as comparisonHook from '../hooks/useModelComparison';

vi.mock('../hooks/useModelComparison', () => ({
  useModelComparison: vi.fn()
}));

// Mock react-plotly.js to avoid JSDOM canvas issues
vi.mock('react-plotly.js', () => ({
  default: () => <div data-testid="plotly-mock">Plotly Chart</div>
}));

describe('ModelArena', () => {
  it('renders correctly and expands/collapses', () => {
    vi.spyOn(comparisonHook, 'useModelComparison').mockReturnValue({
      compareData: {
        xgboost: {
          resonant_frequency_hz: { r2: 0.99, mae: 0.01, mse: 0.0001, rmse: 0.01 },
          gain_dbi: { r2: 0.98, mae: 0.02, mse: 0.0004, rmse: 0.02 }
        },
        linear: {
          resonant_frequency_hz: { r2: 0.85, mae: 0.1, mse: 0.01, rmse: 0.1 },
          gain_dbi: { r2: 0.82, mae: 0.15, mse: 0.0225, rmse: 0.15 }
        }
      },
      importanceData: null,
      learningCurvesData: null,
      loading: false,
      error: null
    } as any);

    render(<ModelArena />);
    
    // Should show button
    const expandBtn = screen.getByRole('button', { name: /show ml model analysis/i });
    expect(expandBtn).toBeInTheDocument();
    
    // Content should not be visible initially
    expect(screen.queryByText('Model Leaderboard (Overall R²)')).not.toBeInTheDocument();
    
    // Click to expand
    fireEvent.click(expandBtn);
    
    // Content should now be visible
    expect(screen.getByText('Model Leaderboard (Overall R²)')).toBeInTheDocument();
    expect(screen.getByText(/xgboost/i)).toBeInTheDocument();
    expect(screen.getByText(/linear/i)).toBeInTheDocument();
  });
});
