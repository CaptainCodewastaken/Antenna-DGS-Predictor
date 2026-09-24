import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Plot from 'react-plotly.js';
import { GlassCard } from '../ui/GlassCard';
import { useModelComparison } from '../../hooks/useModelComparison';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import './ModelComparison.css';

const FEATURE_NAMES: Record<string, string> = {
  sub_eps_r: 'Substrate εr',
  sub_tan_d: 'Substrate Tan δ',
  sub_h: 'Substrate Height',
  sub_size: 'Substrate Size',
  patch_l: 'Patch Length',
  patch_w: 'Patch Width',
  feed_w: 'Feed Width',
  feed_inset: 'Feed Inset'
};

export const ModelArena: React.FC = () => {
  const [expanded, setExpanded] = useState(false);
  const { compareData, importanceData, learningCurvesData, loading, error } = useModelComparison();

  if (error) return null;

  return (
    <div className="model-arena-container">
      <button 
        className="btn btn-outline expand-btn"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
        aria-controls="model-arena-content"
      >
        {expanded ? 'Hide ML Model Analysis' : 'Show ML Model Analysis'}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div 
            id="model-arena-content" 
            className="model-arena-content"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ type: 'spring', bounce: 0.15, duration: 0.5 }}
            style={{ overflow: 'hidden' }}
          >
            {loading ? (
              <LoadingSpinner size="lg" />
            ) : (
              <>
                {/* Leaderboard & Metrics */}
                <div className="arena-row">
                  <GlassCard className="arena-card leaderboard">
                    <h3>Model Leaderboard (Overall R²)</h3>
                    <table className="metrics-table">
                      <thead>
                        <tr>
                          <th>Rank</th>
                          <th>Model</th>
                          <th>Freq R²</th>
                          <th>Gain R²</th>
                        </tr>
                      </thead>
                      <tbody>
                        {compareData && Object.entries(compareData)
                          .sort((a: any, b: any) => {
                            const scoreA = (a[1].resonant_frequency_hz?.r2 || 0) + (a[1].gain_dbi?.r2 || 0);
                            const scoreB = (b[1].resonant_frequency_hz?.r2 || 0) + (b[1].gain_dbi?.r2 || 0);
                            return scoreB - scoreA;
                          })
                          .map(([model, metrics]: [string, any], idx) => (
                            <tr key={model}>
                              <td>{idx + 1}</td>
                              <td style={{ textTransform: 'capitalize' }}>{model.replace('_', ' ')}</td>
                              <td>{metrics.resonant_frequency_hz?.r2?.toFixed(4)}</td>
                              <td>{metrics.gain_dbi?.r2?.toFixed(4)}</td>
                            </tr>
                          ))
                        }
                      </tbody>
                    </table>
                  </GlassCard>
                </div>

                {/* Charts Row */}
                <div className="arena-row charts-row">
                  {/* Feature Importance (using XGBoost as representative) */}
                  <GlassCard className="arena-card chart-card">
                    {importanceData?.xgboost?.resonant_frequency_hz && (
                      <Plot
                        data={[{
                          type: 'bar',
                          x: Object.values(importanceData.xgboost.resonant_frequency_hz).slice(0, 8) as number[],
                          y: Object.keys(importanceData.xgboost.resonant_frequency_hz).slice(0, 8).map(k => FEATURE_NAMES[k] || k),
                          orientation: 'h',
                          marker: { color: '#3b82f6' }
                        }]}
                        layout={{
                          title: { text: 'Top Features (Frequency)', font: { color: '#f8fafc', family: 'Inter' } },
                          paper_bgcolor: 'transparent',
                          plot_bgcolor: 'transparent',
                          margin: { l: 140, r: 20, t: 40, b: 40 },
                          xaxis: { color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.1)' },
                          yaxis: { color: '#94a3b8', autorange: 'reversed' }
                        }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%', minHeight: '300px' }}
                        config={{ displayModeBar: false }}
                      />
                    )}
                  </GlassCard>

                  {/* Learning Curves (using XGBoost as representative) */}
                  <GlassCard className="arena-card chart-card">
                    {learningCurvesData?.xgboost?.resonant_frequency_hz && (
                      <Plot
                        data={[
                          {
                            x: learningCurvesData.xgboost.resonant_frequency_hz.train_sizes,
                            y: learningCurvesData.xgboost.resonant_frequency_hz.train_scores_mean,
                            type: 'scatter',
                            mode: 'lines+markers',
                            name: 'Train',
                            line: { color: '#3b82f6' }
                          },
                          {
                            x: learningCurvesData.xgboost.resonant_frequency_hz.train_sizes,
                            y: learningCurvesData.xgboost.resonant_frequency_hz.test_scores_mean,
                            type: 'scatter',
                            mode: 'lines+markers',
                            name: 'Validation',
                            line: { color: '#10b981' }
                          }
                        ]}
                        layout={{
                          title: { text: 'Learning Curve (XGBoost)', font: { color: '#f8fafc', family: 'Inter' } },
                          paper_bgcolor: 'transparent',
                          plot_bgcolor: 'transparent',
                          margin: { l: 50, r: 20, t: 40, b: 40 },
                          xaxis: { title: 'Training Samples', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.1)' },
                          yaxis: { title: 'R² Score', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.1)' },
                          legend: { font: { color: '#f8fafc' }, bgcolor: 'transparent' }
                        }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%', minHeight: '300px' }}
                        config={{ displayModeBar: false }}
                      />
                    )}
                  </GlassCard>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
