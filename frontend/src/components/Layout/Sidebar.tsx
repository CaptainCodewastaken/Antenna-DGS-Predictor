import React from 'react';
import './Sidebar.css';
import type { AntennaConfig } from '../../hooks/useAntennaConfig';

interface SidebarProps {
  config: AntennaConfig;
  updateSubstrate: (updates: Partial<AntennaConfig['substrate']>) => void;
  updatePatch: (updates: Partial<AntennaConfig['patch']>) => void;
  updateFeed: (updates: Partial<AntennaConfig['feed']>) => void;
  addSlot: () => void;
  removeSlot: (id: string) => void;
  updateSlot: (id: string, updates: Partial<any>) => void;
}

const PRESETS = [
  { label: 'FR4', eps_r: 4.4, tan_d: 0.02 },
  { label: 'Rogers RT/duroid 5880', eps_r: 2.2, tan_d: 0.0009 },
  { label: 'Air', eps_r: 1.0, tan_d: 0.0 },
];

export const Sidebar: React.FC<SidebarProps> = ({
  config,
  updateSubstrate,
  updatePatch,
  updateFeed,
  addSlot,
  removeSlot,
  updateSlot
}) => {
  const handlePresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const preset = PRESETS.find(p => p.label === e.target.value);
    if (preset) {
      updateSubstrate({ epsilon_r: preset.eps_r, tan_delta: preset.tan_d });
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Configuration</h2>
      </div>

      <div className="sidebar-section">
        <h3>Substrate</h3>
        <div className="control-group">
          <label htmlFor="material-preset">Material Preset</label>
          <select id="material-preset" className="control-input" onChange={handlePresetChange} defaultValue="FR4">
            {PRESETS.map(p => <option key={p.label} value={p.label}>{p.label}</option>)}
          </select>
        </div>
        
        <div className="control-group">
          <label htmlFor="sub-height">Height (mm): {config.substrate.height_mm}</label>
          <input 
            id="sub-height"
            type="range" min="0.1" max="5.0" step="0.1" 
            value={config.substrate.height_mm}
            onChange={(e) => updateSubstrate({ height_mm: parseFloat(e.target.value) })}
          />
        </div>
        <div className="control-group">
          <label htmlFor="sub-width">Width (mm): {config.substrate.width_mm}</label>
          <input 
            id="sub-width"
            type="range" min="20" max="100" step="1" 
            value={config.substrate.width_mm}
            onChange={(e) => updateSubstrate({ width_mm: parseFloat(e.target.value) })}
          />
        </div>
        <div className="control-group">
          <label htmlFor="sub-length">Length (mm): {config.substrate.length_mm}</label>
          <input 
            id="sub-length"
            type="range" min="20" max="100" step="1" 
            value={config.substrate.length_mm}
            onChange={(e) => updateSubstrate({ length_mm: parseFloat(e.target.value) })}
          />
        </div>
      </div>

      <div className="sidebar-section">
        <h3>Patch & Feed</h3>
        <div className="control-group">
          <label htmlFor="patch-width">Patch Width (mm): {config.patch.width_mm}</label>
          <input 
            id="patch-width"
            type="range" min="10" max={config.substrate.width_mm} step="0.5" 
            value={config.patch.width_mm}
            onChange={(e) => updatePatch({ width_mm: parseFloat(e.target.value) })}
          />
        </div>
        <div className="control-group">
          <label htmlFor="patch-length">Patch Length (mm): {config.patch.length_mm}</label>
          <input 
            id="patch-length"
            type="range" min="10" max={config.substrate.length_mm} step="0.5" 
            value={config.patch.length_mm}
            onChange={(e) => updatePatch({ length_mm: parseFloat(e.target.value) })}
          />
        </div>
        <div className="control-group">
          <label htmlFor="feed-width">Feed Width (mm): {config.feed.width_mm}</label>
          <input 
            id="feed-width"
            type="range" min="0.5" max="10" step="0.1" 
            value={config.feed.width_mm}
            onChange={(e) => updateFeed({ width_mm: parseFloat(e.target.value) })}
          />
        </div>
        <div className="control-group">
          <label htmlFor="feed-inset">Feed Inset (mm): {config.feed.inset_mm}</label>
          <input 
            id="feed-inset"
            type="range" min="0" max={config.patch.length_mm / 2} step="0.5" 
            value={config.feed.inset_mm}
            onChange={(e) => updateFeed({ inset_mm: parseFloat(e.target.value) })}
          />
        </div>
      </div>

      <div className="sidebar-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>DGS Slots</h3>
          <button 
            className="btn btn-outline btn-sm" 
            onClick={addSlot}
            disabled={config.slots.length >= 2}
            aria-label="Add DGS Slot"
          >
            + Add
          </button>
        </div>
        
        {config.slots.map((slot, index) => (
          <div key={slot.id} className="slot-card glass-panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <h4>Slot {index + 1}</h4>
              <button 
                className="btn btn-sm" 
                onClick={() => removeSlot(slot.id)}
                aria-label={`Remove slot ${index + 1}`}
              >
                X
              </button>
            </div>
            
            <div className="control-group">
              <label htmlFor={`slot-width-${slot.id}`}>Width (mm): {slot.width_mm}</label>
              <input 
                id={`slot-width-${slot.id}`}
                type="range" min="1" max="20" step="0.5" 
                value={slot.width_mm}
                onChange={(e) => updateSlot(slot.id, { width_mm: parseFloat(e.target.value) })}
              />
            </div>
            <div className="control-group">
              <label htmlFor={`slot-length-${slot.id}`}>Length (mm): {slot.length_mm}</label>
              <input 
                id={`slot-length-${slot.id}`}
                type="range" min="1" max="40" step="0.5" 
                value={slot.length_mm}
                onChange={(e) => updateSlot(slot.id, { length_mm: parseFloat(e.target.value) })}
              />
            </div>
            <div className="control-group">
              <label htmlFor={`slot-x-${slot.id}`}>X Position (mm): {slot.x_mm}</label>
              <input 
                id={`slot-x-${slot.id}`}
                type="range" min={-(config.substrate.width_mm / 2)} max={config.substrate.width_mm / 2} step="0.5" 
                value={slot.x_mm}
                onChange={(e) => updateSlot(slot.id, { x_mm: parseFloat(e.target.value) })}
              />
            </div>
            <div className="control-group">
              <label htmlFor={`slot-y-${slot.id}`}>Y Position (mm): {slot.y_mm}</label>
              <input 
                id={`slot-y-${slot.id}`}
                type="range" min={-(config.substrate.length_mm / 2)} max={config.substrate.length_mm / 2} step="0.5" 
                value={slot.y_mm}
                onChange={(e) => updateSlot(slot.id, { y_mm: parseFloat(e.target.value) })}
              />
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
};
