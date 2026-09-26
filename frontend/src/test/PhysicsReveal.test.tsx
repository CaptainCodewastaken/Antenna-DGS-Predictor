import { render, screen, waitFor } from '@testing-library/react';
import { PhysicsReveal } from '../components/Predictions/PhysicsReveal';
import { describe, it, expect, vi } from 'vitest';

// Mock Plotly and fetch to avoid errors in JSDOM
vi.mock('react-plotly.js', () => ({
  default: () => <div>Plotly Mock</div>
}));

// Mock API client
vi.mock('../../api/client', () => ({
  getDGSCircuit: vi.fn().mockResolvedValue({
    L_nH: 1.5,
    C_pF: 0.5,
    f_resonant_ghz: 2.4,
    delta_f_mhz: -100
  })
}));

const mockConfig = {
  substrate: { height_mm: 1.6, epsilon_r: 4.4, tan_delta: 0.02, width_mm: 60, length_mm: 60 },
  patch: { width_mm: 38, length_mm: 29 },
  feed: { width_mm: 3.0, inset_mm: 0 },
  slots: []
};

const mockData = {
  physics_baseline: {
    resonant_frequency_hz: 2.4e9,
    gain_dbi: 5.0,
    bandwidth_hz: 50e6,
    radiation_efficiency: 0.8,
    eps_eff: 4.1,
    delta_l_meters: 0.0008,
    l_eff_meters: 0.0306
  },
  ml_predictions: {}
};

describe('PhysicsReveal', () => {
  it('does not render when not expanded', () => {
    const { container } = render(
      <PhysicsReveal 
        config={mockConfig} 
        data={mockData} 
        expanded={false} 
        onClose={() => {}} 
      />
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders cavity model equations when expanded', async () => {
    render(
      <PhysicsReveal 
        config={mockConfig} 
        data={mockData} 
        expanded={true} 
        onClose={() => {}} 
      />
    );
    
    // Wait for async update to settle
    await waitFor(() => {
      expect(screen.getByText(/Physics Under Glass/i)).toBeInTheDocument();
    });
    
    // Check for base equations
    expect(screen.getByText(/Physics Under Glass/i)).toBeInTheDocument();
    expect(screen.getByText(/Cavity Model Approximation/i)).toBeInTheDocument();
    
    // Check specific values
    expect(screen.getAllByText(/ε/)[0]).toBeInTheDocument(); // eps_eff symbol
    expect(screen.getByText(/2.400 GHz/)).toBeInTheDocument(); // frequency
  });

  it('shows no-slot message when slots are empty', async () => {
    render(
      <PhysicsReveal 
        config={mockConfig} 
        data={mockData} 
        expanded={true} 
        onClose={() => {}} 
      />
    );
    
    await waitFor(() => {
      expect(screen.getByText(/Add a slot to view the LC circuit/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/Add a slot to view the LC circuit/i)).toBeInTheDocument();
  });
});
