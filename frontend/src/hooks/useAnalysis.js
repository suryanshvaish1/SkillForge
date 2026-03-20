import { useState, useCallback } from 'react';
import { analyseDocuments } from '../utils/api';

export function useAnalysis() {
  const [state, setState] = useState({
    loading: false,
    error: null,
    result: null,
  });

  const analyse = useCallback(async (inputs) => {
    setState({ loading: true, error: null, result: null });
    try {
      const result = await analyseDocuments(inputs);
      setState({ loading: false, error: null, result });
      return result;
    } catch (err) {
      setState({ loading: false, error: err.message, result: null });
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ loading: false, error: null, result: null });
  }, []);

  return { ...state, analyse, reset };
}
