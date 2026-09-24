import { useState, useEffect, useRef } from 'react';
import { predict } from '../api/client';
import type { PredictResponse } from '../api/client';
import type { AntennaConfig } from './useAntennaConfig';

export function usePrediction(config: AntennaConfig, debounceMs = 300) {
  const [data, setData] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const debounceTimer = useRef<number | null>(null);

  useEffect(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    setLoading(true);
    
    debounceTimer.current = window.setTimeout(async () => {
      try {
        const result = await predict(config);
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    }, debounceMs);

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [config, debounceMs]);

  return { data, loading, error };
}
