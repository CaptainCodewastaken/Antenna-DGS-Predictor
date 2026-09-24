import { useState, useCallback } from 'react';

export interface DGSSlot {
  id: string;
  width_mm: number;
  length_mm: number;
  x_mm: number;
  y_mm: number;
}

export interface AntennaConfig {
  substrate: {
    epsilon_r: number;
    tan_delta: number;
    height_mm: number;
    width_mm: number;
    length_mm: number;
  };
  patch: {
    width_mm: number;
    length_mm: number;
  };
  feed: {
    width_mm: number;
    inset_mm: number;
  };
  slots: DGSSlot[];
}

const DEFAULT_CONFIG: AntennaConfig = {
  substrate: {
    epsilon_r: 4.4,
    tan_delta: 0.02,
    height_mm: 1.6,
    width_mm: 60.0,
    length_mm: 60.0,
  },
  patch: {
    width_mm: 38.0,
    length_mm: 29.0,
  },
  feed: {
    width_mm: 3.0,
    inset_mm: 8.0,
  },
  slots: [],
};

export function useAntennaConfig() {
  const [config, setConfig] = useState<AntennaConfig>(DEFAULT_CONFIG);

  const updateSubstrate = useCallback((updates: Partial<AntennaConfig['substrate']>) => {
    setConfig(prev => ({
      ...prev,
      substrate: { ...prev.substrate, ...updates }
    }));
  }, []);

  const updatePatch = useCallback((updates: Partial<AntennaConfig['patch']>) => {
    setConfig(prev => ({
      ...prev,
      patch: { ...prev.patch, ...updates }
    }));
  }, []);

  const updateFeed = useCallback((updates: Partial<AntennaConfig['feed']>) => {
    setConfig(prev => ({
      ...prev,
      feed: { ...prev.feed, ...updates }
    }));
  }, []);

  const addSlot = useCallback(() => {
    setConfig(prev => {
      if (prev.slots.length >= 2) return prev;
      const newSlot: DGSSlot = {
        id: Math.random().toString(36).substr(2, 9),
        width_mm: 5.0,
        length_mm: 15.0,
        x_mm: 0.0,
        y_mm: 10.0
      };
      return { ...prev, slots: [...prev.slots, newSlot] };
    });
  }, []);

  const removeSlot = useCallback((id: string) => {
    setConfig(prev => ({
      ...prev,
      slots: prev.slots.filter(s => s.id !== id)
    }));
  }, []);

  const updateSlot = useCallback((id: string, updates: Partial<Omit<DGSSlot, 'id'>>) => {
    setConfig(prev => ({
      ...prev,
      slots: prev.slots.map(s => s.id === id ? { ...s, ...updates } : s)
    }));
  }, []);

  return {
    config,
    updateSubstrate,
    updatePatch,
    updateFeed,
    addSlot,
    removeSlot,
    updateSlot,
  };
}
