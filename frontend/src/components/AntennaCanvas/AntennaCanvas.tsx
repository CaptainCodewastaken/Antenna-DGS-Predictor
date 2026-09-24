import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { AntennaConfig } from '../../hooks/useAntennaConfig';
import './AntennaCanvas.css';

interface AntennaCanvasProps {
  config: AntennaConfig;
}

export const AntennaCanvas: React.FC<AntennaCanvasProps> = ({ config }) => {
  // SVG coordinate system:
  // (0,0) is center of substrate
  // Y goes down (SVG default)
  
  const subW = config.substrate.width_mm;
  const subL = config.substrate.length_mm;
  const patchW = config.patch.width_mm;
  const patchL = config.patch.length_mm;
  const feedW = config.feed.width_mm;
  const feedInset = config.feed.inset_mm;
  const feedL = (subL / 2) - (patchL / 2) + feedInset;

  // ViewBox adds some padding around substrate
  const padding = 20;
  const vbX = -subW / 2 - padding;
  const vbY = -subL / 2 - padding;
  const vbW = subW + padding * 2;
  const vbH = subL + padding * 2;

  return (
    <div className="canvas-container glass-panel">
      <h3 className="canvas-title">Top-Down Schematic</h3>
      
      <svg 
        viewBox={`${vbX} ${vbY} ${vbW} ${vbH}`}
        className="antenna-svg"
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-labelledby="antenna-svg-title"
      >
        <title id="antenna-svg-title">Top-down schematic of the antenna with width {subW}mm and length {subL}mm</title>
        <defs>
          <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="0.5" />
          </pattern>
        </defs>

        {/* Background Grid */}
        <rect x={vbX} y={vbY} width={vbW} height={vbH} fill="url(#grid)" />

        {/* Substrate / Ground Plane */}
        <motion.rect 
          animate={{ x: -subW / 2, y: -subL / 2, width: subW, height: subL }}
          transition={{ type: "spring", bounce: 0, duration: 0.4 }}
          className="svg-substrate" 
        />

        {/* DGS Slots (dashed outline, drawn below patch) */}
        <AnimatePresence>
          {config.slots.map(slot => (
            <motion.rect
              key={slot.id}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ 
                opacity: 1, 
                scale: 1,
                x: slot.x_mm - slot.width_mm / 2,
                y: slot.y_mm - slot.length_mm / 2,
                width: slot.width_mm,
                height: slot.length_mm
              }}
              exit={{ opacity: 0, scale: 0.5 }}
              transition={{ type: "spring", bounce: 0, duration: 0.4 }}
              className="svg-slot"
            />
          ))}
        </AnimatePresence>

        {/* Patch */}
        <motion.path 
          animate={{ d: `
            M ${-patchW/2} ${-patchL/2} 
            L ${patchW/2} ${-patchL/2} 
            L ${patchW/2} ${patchL/2} 
            L ${feedW/2} ${patchL/2}
            L ${feedW/2} ${patchL/2 - feedInset}
            L ${-feedW/2} ${patchL/2 - feedInset}
            L ${-feedW/2} ${patchL/2}
            L ${-patchW/2} ${patchL/2}
            Z
          `}} 
          transition={{ type: "spring", bounce: 0, duration: 0.4 }}
          className="svg-patch" 
        />

        {/* Feed Line */}
        <motion.rect 
          animate={{ 
            x: -feedW / 2, 
            y: patchL / 2 - feedInset, 
            width: feedW, 
            height: feedL 
          }} 
          transition={{ type: "spring", bounce: 0, duration: 0.4 }}
          className="svg-feed" 
        />

        {/* Dimensions */}
        <g className="svg-dimensions">
          {/* Substrate Width */}
          <motion.line 
            animate={{ x1: -subW/2, y1: subL/2 + 10, x2: subW/2, y2: subL/2 + 10 }} 
            transition={{ type: "spring", bounce: 0, duration: 0.4 }}
            markerEnd="url(#arrow)" markerStart="url(#arrow)" 
          />
          <motion.text 
            animate={{ x: 0, y: subL/2 + 18 }} 
            transition={{ type: "spring", bounce: 0, duration: 0.4 }}
          >
            W: {subW}mm
          </motion.text>
          
          {/* Substrate Length */}
          <motion.line 
            animate={{ x1: -subW/2 - 10, y1: -subL/2, x2: -subW/2 - 10, y2: subL/2 }} 
            transition={{ type: "spring", bounce: 0, duration: 0.4 }}
            markerEnd="url(#arrow)" markerStart="url(#arrow)" 
          />
          <motion.text 
            animate={{ x: -subW/2 - 15, y: 0 }} 
            style={{ transformOrigin: "center" }}
            transform={`rotate(-90, ${-subW/2 - 15}, 0)`}
            transition={{ type: "spring", bounce: 0, duration: 0.4 }}
          >
            L: {subL}mm
          </motion.text>
        </g>

        {/* Arrow markers for dimensions */}
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.5)" />
          </marker>
        </defs>

      </svg>
    </div>
  );
};
