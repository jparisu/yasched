/* eslint-disable react-refresh/only-export-components -- provider + hook colocated by design */
import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  createElement,
  deleteElement,
  fetchElement,
  fetchElements,
  fetchMeta,
  fetchValidation,
  reloadDatabase,
  updateElement,
} from './api';
import {
  AttributeDefinitionDTO,
  ElementDTO,
  ElementSpec,
  MetaDTO,
  ValidationDTO,
} from './types';
import { indexById } from './lib/elements';

interface DataApi {
  elements: ElementDTO[];
  byId: Record<string, ElementDTO>;
  definitions: AttributeDefinitionDTO[];
  meta: MetaDTO | null;
  validation: ValidationDTO | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
  /** Create or replace (also the virtual -> real promotion path). */
  save: (spec: ElementSpec) => Promise<void>;
  remove: (id: string) => Promise<void>;
  /** Merge attribute changes into one element's OWN values (promotes if virtual). */
  patchAttributes: (id: string, changes: Record<string, unknown>) => Promise<void>;
}

const DataContext = createContext<DataApi>({
  elements: [],
  byId: {},
  definitions: [],
  meta: null,
  validation: null,
  loading: true,
  error: null,
  reload: () => {},
  save: async () => {},
  remove: async () => {},
  patchAttributes: async () => {},
});

export function DataProvider({ children }: { children: ReactNode }) {
  const [elements, setElements] = useState<ElementDTO[]>([]);
  const [definitions, setDefinitions] = useState<AttributeDefinitionDTO[]>([]);
  const [meta, setMeta] = useState<MetaDTO | null>(null);
  const [validation, setValidation] = useState<ValidationDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([fetchElements(), fetchMeta(), fetchValidation()])
      .then(([payload, m, val]) => {
        setElements(payload.elements);
        setDefinitions(payload.definitions);
        setMeta(m);
        setValidation(val);
        setError(null);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(load, [load]);

  const save = useCallback(
    async (spec: ElementSpec) => {
      const { id, ...rest } = spec;
      const exists = elements.some((e) => e.id === id && !e.virtual);
      if (exists) {
        await updateElement(id, rest);
      } else {
        await createElement(spec);
      }
      load();
    },
    [elements, load],
  );

  const remove = useCallback(
    async (id: string) => {
      await deleteElement(id);
      load();
    },
    [load],
  );

  const patchAttributes = useCallback(
    async (id: string, changes: Record<string, unknown>) => {
      let spec: ElementSpec;
      try {
        const raw = await fetchElement(id); // raw OWN values (404 for virtual)
        spec = {
          id: raw.id,
          type: raw.type,
          directParents: raw.directParents,
          attributes: { ...(raw.attributes ?? {}) },
          layout: raw.layout,
        };
      } catch {
        const dto = elements.find((e) => e.id === id);
        if (!dto) throw new Error(`Unknown element ${id}`);
        spec = { id, type: dto.type, directParents: dto.mainParent ? [dto.mainParent] : [], attributes: {} };
      }
      spec.attributes = { ...(spec.attributes ?? {}), ...changes };
      await save(spec);
    },
    [elements, save],
  );

  const reload = useCallback(() => {
    reloadDatabase().then(load).catch(() => load());
  }, [load]);

  const byId = useMemo(() => indexById(elements), [elements]);

  const value: DataApi = {
    elements,
    byId,
    definitions,
    meta,
    validation,
    loading,
    error,
    reload,
    save,
    remove,
    patchAttributes,
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useData(): DataApi {
  return useContext(DataContext);
}
