import React from 'react';
import Plot from 'react-plotly.js';
import type { PatternResponse } from '../../api/client';
import { GlassCard } from '../ui/GlassCard';

interface Pattern3DProps {
  data: PatternResponse | null;
}

export const Pattern3D: React.FC<Pattern3DProps> = ({ data }) => {
  if (!data) return <GlassCard>Loading 3D Pattern...</GlassCard>;

  // Convert spherical (theta, phi, r=gain) to Cartesian (x,y,z) for 3D plot
  const x: number[][] = [];
  const y: number[][] = [];
  const z: number[][] = [];

  for (let i = 0; i < data.theta.length; i++) {
    const thetaRad = data.theta[i] * (Math.PI / 180);
    const xRow: number[] = [];
    const yRow: number[] = [];
    const zRow: number[] = [];
    
    for (let j = 0; j < data.phi.length; j++) {
      const phiRad = data.phi[j] * (Math.PI / 180);
      const r = Math.max(data.gain_3d[i][j], 0); // clamp to 0 for radius to avoid inward folding

      xRow.push(r * Math.sin(thetaRad) * Math.cos(phiRad));
      yRow.push(r * Math.sin(thetaRad) * Math.sin(phiRad));
      zRow.push(r * Math.cos(thetaRad));
    }
    x.push(xRow);
    y.push(yRow);
    z.push(zRow);
  }

  const surfaceTrace = {
    x,
    y,
    z,
    type: 'surface' as const,
    surfacecolor: data.gain_3d,
    colorscale: 'Viridis' as const,
    showscale: false
  };

  const layout = {
    title: {
      text: '3D Radiation Surface',
      font: { color: '#f8fafc', family: 'Inter' }
    },
    paper_bgcolor: 'transparent',
    margin: { l: 0, r: 0, t: 30, b: 0 },
    scene: {
      xaxis: { title: 'X', color: '#94a3b8', backgroundcolor: 'transparent', gridcolor: 'rgba(255,255,255,0.1)', showbackground: false },
      yaxis: { title: 'Y', color: '#94a3b8', backgroundcolor: 'transparent', gridcolor: 'rgba(255,255,255,0.1)', showbackground: false },
      zaxis: { title: 'Z', color: '#94a3b8', backgroundcolor: 'transparent', gridcolor: 'rgba(255,255,255,0.1)', showbackground: false },
      camera: {
        eye: { x: 1.5, y: 1.5, z: 1.5 }
      }
    },
    autosize: true
  };

  return (
    <GlassCard className="plot-card">
      <Plot
        data={[surfaceTrace]}
        layout={layout}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%', minHeight: '300px' }}
        config={{ displayModeBar: false }}
      />
    </GlassCard>
  );
};
