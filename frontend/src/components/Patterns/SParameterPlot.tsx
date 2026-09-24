import React from 'react';
import Plot from 'react-plotly.js';
import type { SParameterResponse } from '../../api/client';
import { GlassCard } from '../ui/GlassCard';

interface SParameterPlotProps {
  data: SParameterResponse | null;
}

export const SParameterPlot: React.FC<SParameterPlotProps> = ({ data }) => {
  if (!data) return <GlassCard>Loading S11...</GlassCard>;

  const trace = {
    x: data.frequencies_ghz,
    y: data.s11_db,
    type: 'scatter' as const,
    mode: 'lines' as const,
    name: 'S₁₁',
    line: { color: '#3b82f6', width: 2 }
  };

  const thresholdLine = {
    x: [Math.min(...data.frequencies_ghz), Math.max(...data.frequencies_ghz)],
    y: [-10, -10],
    type: 'scatter' as const,
    mode: 'lines' as const,
    name: '-10 dB',
    line: { color: 'rgba(239, 68, 68, 0.5)', width: 2, dash: 'dash' }
  };

  const layout = {
    title: {
      text: 'S₁₁ Return Loss',
      font: { color: '#f8fafc', family: 'Inter' }
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    xaxis: {
      title: 'Frequency (GHz)',
      color: '#94a3b8',
      gridcolor: 'rgba(255,255,255,0.1)'
    },
    yaxis: {
      title: 'S₁₁ (dB)',
      color: '#94a3b8',
      gridcolor: 'rgba(255,255,255,0.1)'
    },
    margin: { l: 50, r: 20, t: 40, b: 40 },
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
        data={[trace, thresholdLine] as any}
        layout={layout}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%', minHeight: '300px' }}
        config={{ displayModeBar: false }}
      />
    </GlassCard>
  );
};
