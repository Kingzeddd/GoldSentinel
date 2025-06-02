import { useState, useEffect } from 'react';
import { detectionService, Detection } from '../services';

export const useDetections = (params?: any) => {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    const fetchDetections = async () => {
      try {
        setLoading(true);
        const { results, count } = await detectionService.getDetections(params);
        setDetections(results);
        setTotalCount(count);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Une erreur est survenue');
      } finally {
        setLoading(false);
      }
    };

    fetchDetections();
  }, [params]);

  const validateDetection = async (id: number, status: string) => {
    try {
      const updated = await detectionService.validateDetection(id, status);
      setDetections(prev => 
        prev.map(d => d.id === id ? updated : d)
      );
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la validation');
      return false;
    }
  };

  return {
    detections,
    loading,
    error,
    totalCount,
 