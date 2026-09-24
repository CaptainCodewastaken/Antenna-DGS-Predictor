import { useState, useEffect } from 'react';
import { getModelCompare, getFeatureImportance, getLearningCurves } from '../api/client';

export function useModelComparison() {
  const [compareData, setCompareData] = useState<any>(null);
  const [importanceData, setImportanceData] = useState<any>(null);
  const [learningCurvesData, setLearningCurvesData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [cmp, imp, lc] = await Promise.all([
          getModelCompare(),
          getFeatureImportance(),
          getLearningCurves()
        ]);
        setCompareData(cmp);
        setImportanceData(imp);
        setLearningCurvesData(lc);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load model data'));
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  return { compareData, importanceData, learningCurvesData, loading, error };
}
