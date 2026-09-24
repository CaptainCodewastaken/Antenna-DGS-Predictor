import { useState, useEffect } from 'react';
import { getPattern, getSParameter } from '../api/client';
import type { PatternResponse, SParameterResponse } from '../api/client';
import type { AntennaConfig } from './useAntennaConfig';

export function usePattern(config: AntennaConfig, debounceMs = 500) {
  const [patternData, setPatternData] = useState<PatternResponse | null>(null);
  const [sParamData, setSParamData] = useState<SParameterResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let isMounted = true;
    
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const [pattern, sParam] = await Promise.all([
          getPattern(config),
          getSParameter(config)
        ]);
        if (isMounted) {
          setPatternData(pattern);
          setSParamData(sParam);
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

  return { patternData, sParamData, loading, error };
}
