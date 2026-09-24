import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { PredictResponse } from '../../api/client';
import { getDGSCircuit } from '../../api/client';
import type { DGSCircuitResponse } from '../../api/client';
import type { AntennaConfig } from '../../hooks/useAntennaConfig';
import { GlassCard } from '../ui/GlassCard';
import './PhysicsReveal.css';

interface PhysicsRevealProps {
  config: AntennaConfig;
  data: PredictResponse | null;
  expanded: boolean;
  onClose: () => void;
}

export const PhysicsReveal: React.FC<PhysicsRevealProps> = ({ config, data, expanded, onClose }) => {
  const [dgsCircuits, setDgsCircuits] = useState<DGSCircuitResponse[]>([]);
  const closeBtnRef = React.useRef<HTMLButtonElement>(null);
  
  useEffect(() => {
    if (!expanded) return;
    
    // Focus management for accessibility
    closeBtnRef.current?.focus();
    
    // Fetch DGS circuit values for all slots
    const fetchDgs = async () => {
      try {
        const promises = config.slots.map(s => getDGSCircuit(
          { width_mm: s.width_mm, length_mm: s.length_mm, x_mm: s.x_mm, y_mm: s.y_mm },
          config.substrate.height_mm,
          config.substrate.epsilon_r
        ));
        const results = await Promise.all(promises);
        setDgsCircuits(results);
      } catch (e) {
        console.error('Failed to fetch DGS circuits', e);
      }
    };
    
    fetchDgs();
  }, [expanded, config]);

  const w = config.patch.width_mm * 1e-3;
  const h = config.substrate.height_mm * 1e-3;
  const eps_r = config.substrate.epsilon_r;
  const l = config.patch.length_mm * 1e-3;
  const eps_eff = (eps_r + 1) / 2 + ((eps_r - 1) / 2) * Math.pow(1 + 12 * (h / w), -0.5);
  const delta_l = h * 0.412 * ((eps_eff + 0.3) * (w / h + 0.264)) / ((eps_eff - 0.258) * (w / h + 0.8));
  const l_eff = l + 2 * delta_l;

  return (
    <AnimatePresence>
      {expanded && data && (
        <motion.div 
          className="physics-reveal-container" 
          role="region" 
          aria-label="Physics formulas"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
          style={{ overflow: 'hidden' }}
        >
          <GlassCard className="physics-reveal-card">
            <div className="physics-reveal-header">
              <h3>Physics Under Glass (Layer 2)</h3>
              <button ref={closeBtnRef} className="btn btn-sm btn-outline" onClick={onClose} aria-label="Close physics panel">Close</button>
            </div>

            <div className="physics-reveal-grid">
              {/* Cavity Model Column */}
              <div className="physics-column">
                <h4>Cavity Model Approximation</h4>
                <div className="equation-box">
                  <p>ε<sub>eff</sub> = {eps_eff.toFixed(3)}</p>
                  <p>ΔL = {(delta_l * 1e3).toFixed(3)} mm</p>
                  <p>L<sub>eff</sub> = {(l_eff * 1e3).toFixed(3)} mm</p>
                  <div className="equation-highlight">
                    <p>f<sub>r</sub> = c / (2 × L<sub>eff</sub> × √ε<sub>eff</sub>)</p>
                    <p><strong>f<sub>r</sub> = {(data.physics_baseline.resonant_frequency_hz / 1e9).toFixed(3)} GHz</strong></p>
                  </div>
                </div>
              </div>

              {/* DGS Circuit Column */}
              {config.slots.length > 0 && (
                <div className="physics-column">
                  <h4>DGS Equivalent Circuit</h4>
                  {dgsCircuits.map((c, idx) => (
                    <div key={idx} className="circuit-box">
                      <h5>Slot {idx + 1}</h5>
                      <div className="circuit-svg">
                        <svg viewBox="0 0 200 80" width="100%" height="80">
                          {/* L and C in parallel */}
                          <path d="M 20 40 L 40 40 L 40 20 L 60 20 C 65 10, 75 10, 80 20 C 85 10, 95 10, 100 20 C 105 10, 115 10, 120 20 L 140 20 L 140 40 L 160 40" fill="transparent" stroke="var(--accent-primary)" strokeWidth="2" />
                          
                          <path d="M 40 40 L 40 60 L 80 60" fill="transparent" stroke="var(--accent-success)" strokeWidth="2" />
                          <line x1="80" y1="50" x2="80" y2="70" stroke="var(--accent-success)" strokeWidth="2" />
                          <line x1="100" y1="50" x2="100" y2="70" stroke="var(--accent-success)" strokeWidth="2" />
                          <path d="M 100 60 L 140 60 L 140 40" fill="transparent" stroke="var(--accent-success)" strokeWidth="2" />
                          
                          <text x="90" y="15" fill="var(--text-secondary)" fontSize="10" textAnchor="middle">L = {c.L_nH.toFixed(2)} nH</text>
                          <text x="90" y="75" fill="var(--text-secondary)" fontSize="10" textAnchor="middle">C = {c.C_pF.toFixed(2)} pF</text>
                        </svg>
                      </div>
                      <p>f<sub>dgs</sub> = {c.f_resonant_ghz.toFixed(2)} GHz</p>
                      <p>Δf (shift) = {c.delta_f_mhz > 0 ? '+' : ''}{c.delta_f_mhz.toFixed(1)} MHz</p>
                    </div>
                  ))}
                </div>
              )}
              
              {config.slots.length === 0 && (
                <div className="physics-column">
                  <h4>DGS Equivalent Circuit</h4>
                  <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>Add a slot to view the LC circuit.</p>
                </div>
              )}
            </div>
          </GlassCard>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
