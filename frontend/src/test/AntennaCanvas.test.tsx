import { render, screen } from '@testing-library/react';
import { AntennaCanvas } from '../components/AntennaCanvas/AntennaCanvas';
import { describe, it, expect } from 'vitest';

const mockConfig = {
  substrate: { height_mm: 1.6, epsilon_r: 4.4, tan_delta: 0.02, width_mm: 60, length_mm: 60 },
  patch: { width_mm: 38, length_mm: 29 },
  feed: { width_mm: 3.0, inset_mm: 8.0 },
  slots: [
    { width_mm: 10, length_mm: 2, x_mm: 0, y_mm: 5 }
  ]
};

describe('AntennaCanvas', () => {
  it('renders SVG elements correctly', () => {
    const { container } = render(<AntennaCanvas config={mockConfig} />);
    
    // Check if SVG is rendered
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    
    // Check for ground plane dimensions text
    expect(screen.getByText(/W: 60mm/)).toBeInTheDocument();
    expect(screen.getByText(/L: 60mm/)).toBeInTheDocument();
  });

  it('renders slot elements when slots are present', () => {
    const { container } = render(<AntennaCanvas config={mockConfig} />);
    
    // Check if the slot rect was rendered (it has the svg-slot class)
    const slotRect = container.querySelector('.svg-slot');
    expect(slotRect).toBeInTheDocument();
  });
});
