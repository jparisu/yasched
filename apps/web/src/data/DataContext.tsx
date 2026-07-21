/* eslint-disable react-refresh/only-export-components -- provider + hook colocated by design */
import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react';
import {
  AgendaData,
  Meta,
  ValidationResult,
  fetchAgenda,
  fetchMeta,
  fetchValidation,
} from '../api/client';

interface DataState extends AgendaData {
  loading: boolean;
  error: string | null;
  reload: () => void;
  validation: ValidationResult | null;
  meta: Meta | null;
  readOnly: boolean;
}

const EMPTY: AgendaData = { topics: [], tasks: [], events: [], deadlines: [] };

const DataContext = createContext<DataState>({
  ...EMPTY,
  loading: true,
  error: null,
  reload: () => {},
  validation: null,
  meta: null,
  readOnly: true,
});

export function DataProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<AgendaData>(EMPTY);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([fetchAgenda(), fetchValidation(), fetchMeta()])
      .then(([agenda, val, m]) => {
        setData(agenda);
        setValidation(val);
        setMeta(m);
        setError(null);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(load, [load]);

  return (
    <DataContext.Provider
      value={{
        ...data,
        loading,
        error,
        reload: load,
        validation,
        meta,
        readOnly: meta?.readOnly ?? true,
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

export function useData(): DataState {
  return useContext(DataContext);
}
