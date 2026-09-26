import type { AntennaConfig } from '../hooks/useAntennaConfig';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface PredictResponse {
  physics_baseline: {
    resonant_frequency_hz: number;
    gain_dbi: number;
    bandwidth_hz: number;
    radiation_efficiency: number;
    eps_eff: number;
    delta_l_meters: number;
    l_eff_meters: number;
  };
  ml_predictions: {
    [model_name: string]: {
      resonant_frequency_hz: number;
      gain_dbi: number;
      bandwidth_hz: number;
      radiation_efficiency: number;
    };
  };
}

export async function predict(config: AntennaConfig): Promise<PredictResponse> {
  const payload = {
    substrate: {
      epsilon_r: config.substrate.epsilon_r,
      tan_delta: config.substrate.tan_delta,
      height_mm: config.substrate.height_mm,
      width_mm: config.substrate.width_mm,
      length_mm: config.substrate.length_mm,
    },
    patch: {
      width_mm: config.patch.width_mm,
      length_mm: config.patch.length_mm,
    },
    feed: {
      width_mm: config.feed.width_mm,
      inset_mm: config.feed.inset_mm,
    },
    slots: config.slots.map(s => ({
      width_mm: s.width_mm,
      length_mm: s.length_mm,
      x_mm: s.x_mm,
      y_mm: s.y_mm
    }))
  };

  const response = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json();
  const physics = data.physics;
  // Compute absolute bandwidth from fractional bandwidth and resonant frequency
  physics.bandwidth_hz = physics.bandwidth_fractional * physics.resonant_frequency_hz;

  return {
    physics_baseline: physics,
    ml_predictions: data.ml_predictions
  };
}

export interface PatternResponse {
  theta: number[];
  phi: number[];
  gain_3d: number[][];
  e_plane: { theta: number[], gain: number[] };
  h_plane: { theta: number[], gain: number[] };
}

export async function getPattern(config: AntennaConfig): Promise<PatternResponse> {
  const payload = {
    substrate: {
      epsilon_r: config.substrate.epsilon_r,
      tan_delta: config.substrate.tan_delta,
      height_mm: config.substrate.height_mm,
      width_mm: config.substrate.width_mm,
      length_mm: config.substrate.length_mm,
    },
    patch: {
      width_mm: config.patch.width_mm,
      length_mm: config.patch.length_mm,
    },
    feed: {
      width_mm: config.feed.width_mm,
      inset_mm: config.feed.inset_mm,
    },
    slots: config.slots.map(s => ({
      width_mm: s.width_mm,
      length_mm: s.length_mm,
      x_mm: s.x_mm,
      y_mm: s.y_mm
    }))
  };

  const response = await fetch(`${API_BASE}/pattern?resolution_deg=5`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  if (!response.ok) throw new Error(`API error: ${response.statusText}`);
  const data = await response.json();
  
  return {
    theta: data.theta,
    phi: data.phi,
    gain_3d: data.gain_db,
    e_plane: { theta: data.theta, gain: data.e_plane },
    h_plane: { theta: data.theta, gain: data.h_plane }
  };
}

export interface SParameterResponse {
  frequencies_ghz: number[];
  s11_db: number[];
}

export async function getSParameter(config: AntennaConfig, f_start = 1.0, f_end = 5.0, points = 200): Promise<SParameterResponse> {
  const payload = {
    substrate: {
      epsilon_r: config.substrate.epsilon_r,
      tan_delta: config.substrate.tan_delta,
      height_mm: config.substrate.height_mm,
      width_mm: config.substrate.width_mm,
      length_mm: config.substrate.length_mm,
    },
    patch: {
      width_mm: config.patch.width_mm,
      length_mm: config.patch.length_mm,
    },
    feed: {
      width_mm: config.feed.width_mm,
      inset_mm: config.feed.inset_mm,
    },
    slots: config.slots.map(s => ({
      width_mm: s.width_mm,
      length_mm: s.length_mm,
      x_mm: s.x_mm,
      y_mm: s.y_mm
    }))
  };

  const span_ghz = f_end - f_start;

  const response = await fetch(`${API_BASE}/s-parameter?points=${points}&span_ghz=${span_ghz}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  if (!response.ok) throw new Error(`API error: ${response.statusText}`);
  const data = await response.json();
  
  return {
    frequencies_ghz: data.freq_ghz,
    s11_db: data.s11_db
  };
}

export interface DGSCircuitResponse {
  L_nH: number;
  C_pF: number;
  f_resonant_ghz: number;
  delta_f_mhz: number;
}

export async function getDGSCircuit(slot: { width_mm: number, length_mm: number, x_mm: number, y_mm: number }, substrate_height_mm: number, epsilon_r: number): Promise<DGSCircuitResponse> {
  const response = await fetch(`${API_BASE}/dgs/circuit?substrate_height_mm=${substrate_height_mm}&epsilon_r=${epsilon_r}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(slot)
  });
  if (!response.ok) throw new Error('API error');
  return response.json();
}

export async function getModelCompare() {
  const response = await fetch(`${API_BASE}/models/compare`);
  if (!response.ok) throw new Error('API error');
  return response.json();
}

export async function getFeatureImportance() {
  const response = await fetch(`${API_BASE}/models/feature-importance`);
  if (!response.ok) throw new Error('API error');
  return response.json();
}

export async function getLearningCurves() {
  const response = await fetch(`${API_BASE}/models/learning-curves`);
  if (!response.ok) throw new Error('API error');
  return response.json();
}
