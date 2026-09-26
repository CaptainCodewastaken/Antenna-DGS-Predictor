import React from 'react';
import { motion } from 'framer-motion';
import { GlassCard } from '../ui/GlassCard';
import { AnimatedNumber } from '../ui/AnimatedNumber';
import { LoadingSpinner } from '../ui/LoadingSpinner';
import type { PredictResponse } from '../../api/client';
import './PredictionCards.css';

interface PredictionCardsProps {
  data: PredictResponse | null;
  loading: boolean;
  selectedModel?: string; // 'physics_baseline' or model name like 'xgboost'
}

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', bounce: 0.3 } }
};

export const PredictionCards: React.FC<PredictionCardsProps> = ({ data, loading, selectedModel = 'xgboost' }) => {
  const getMetrics = () => {
    if (!data) return null;
    const base = data.physics_baseline;
    if (selectedModel === 'physics_baseline') {
      return base;
    }
    const ml = data.ml_predictions[selectedModel] as any; // Ignore TS type to get actual runtime keys
    
    // ML returns bandwidth_fractional, so we need to compute bandwidth_hz dynamically
    const freq = ml.resonant_frequency_hz || base.resonant_frequency_hz;
    const fractional_bw = ml.bandwidth_fractional || base.bandwidth_fractional;
    const bandwidth_hz = fractional_bw * freq;
    
    // Efficiency is only in base
    const efficiency = base.radiation_efficiency;

    return {
      resonant_frequency_hz: freq,
      gain_dbi: ml.gain_dbi || base.gain_dbi,
      bandwidth_hz: bandwidth_hz,
      radiation_efficiency: efficiency
    };
  };

  const metrics = getMetrics();

  const cards = [
    { id: 'freq', title: 'Resonant Frequency', value: metrics ? metrics.resonant_frequency_hz / 1e9 : 0, unit: 'GHz', format: (val: number) => val.toFixed(3) },
    { id: 'gain', title: 'Antenna Gain', value: metrics ? metrics.gain_dbi : 0, unit: 'dBi', format: (val: number) => val.toFixed(2) },
    { id: 'bw', title: 'Bandwidth', value: metrics ? metrics.bandwidth_hz / 1e6 : 0, unit: 'MHz', format: (val: number) => val.toFixed(1) },
    { id: 'eff', title: 'Efficiency', value: metrics ? metrics.radiation_efficiency * 100 : 0, unit: '%', format: (val: number) => val.toFixed(1) },
  ];

  return (
    <motion.div 
      className="prediction-cards-container"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {loading && (
        <div className="prediction-overlay">
          <LoadingSpinner size="lg" />
        </div>
      )}
      
      {cards.map(card => (
        <motion.div key={card.id} variants={itemVariants} className="prediction-card-wrapper">
          <GlassCard className={`prediction-card ${card.id}-card`}>
            <h4 className="metric-title">{card.title}</h4>
            <div className="metric-value-container">
              <AnimatedNumber 
                value={card.value} 
                format={card.format} 
                className="metric-big"
              />
              <span className="metric-unit">{card.unit}</span>
            </div>
          </GlassCard>
        </motion.div>
      ))}
    </motion.div>
  );
};
