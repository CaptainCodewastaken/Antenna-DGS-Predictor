import React from 'react';
import Plot from 'react-plotly.js';
import type { PatternResponse } from '../../api/client';
import { GlassCard } from '../ui/GlassCard';

interface PolarPatternProps {
  data: PatternResponse | null;
}

export const PolarPattern: React.FC<PolarPatternProps> = ({ data }) => {
  if (!data) return <GlassCard>Loading Polar Pattern...</GlassCard>;

  const ePlaneTrace = {
    r: data.e_plane.gain,
    theta: data.e_plane.theta,
    type: 'scatterpolar' as const,
    mode: 'lines' as const,
    name: 'E-Plane (φ=0°)',
    line: { color: '#3b82f6', width: 2 }
  };

  const hPlaneTrace = {
    r: data.h_plane.gain,
    theta: data.h_plane.theta,
    type: 'scatterpolar' as const,
    mode: 'lines' as const,
    name: 'H-Plane (φ=90°)',
    line: { color: '#10b981', width: 2 }
  };

  const layout = {
    title: {
      text: '2D Radiation Pattern',
      font: { color: '#f8fafc', family: 'Inter' }
    },
    paper_bgcolor: 'transparent',
    polar: {
      bgcolor: 'rgba(0,0,0,0.2)',
      angularaxis: {
        tickfont: { color: '#94a3b8' },
        linecolor: 'rgba(255,255,255,0.1)'
      },
      radialaxis: {
        tickfont: { color: '#94a3b8' },
        gridcolor: 'rgba(255,255,255,0.1)',
        linecolor: 'rgba(255,255,255,0.1)'
      }
    },
    margin: { l: 40, r: 40, t: 40, b: 40 },
    showlegend: true,
    legend: {
      font: { color: '#f8fafc' },
      bgcolor: 'transparent'
    },
    autosize: true
  };

  return (
    <GlassCard className="plot-card">
      <Plot
        data={[ePlaneTrace, hPlaneTrace]}
        layout={layout}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%', minHeight: '300px' }}
        config={{ displayModeBar: false }}
      />
    </GlassCard>
  );
};
