import { useState, useEffect, useRef } from 'react';
import { getPattern, getSParameter } from '../api/client';
import type { PatternResponse, SParameterResponse } from '../api/client';
import type { AntennaConfig } from './useAntennaConfig';

export function usePattern(config: AntennaConfig, debounceMs = 500) {
  const [patternData, setPatternData] = useState<PatternResponse | null>(null);
  const [sParamData, setSParamData] = useState<SParameterResponse | null>(null);
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
        const [pattern, sParam] = await Promise.all([
          getPattern(config),
          getSParameter(config)
        ]);
        setPatternData(pattern);
        setSParamData(sParam);
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

  return { patternData, sParamData, loading, error };
}
