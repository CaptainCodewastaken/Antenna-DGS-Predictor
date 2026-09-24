import { useState, useEffect } from 'react';
import { predict } from '../api/client';
import type { PredictResponse } from '../api/client';
import type { AntennaConfig } from './useAntennaConfig';

export function usePrediction(config: AntennaConfig, debounceMs = 300) {
  const [data, setData] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const result = await predict(config);
        if (isMounted) {
          setData(result);
          setError(null);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err : new Error('Unknown error'));
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }, debounceMs);

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [config, debounceMs]);

  return { data, loading, error };
}
