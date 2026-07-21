/* eslint-disable react-refresh/only-export-components -- provider + hook colocated by design */
import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { EntityKind } from '../api/client';

export interface ElementSelection {
  kind: EntityKind;
  id: string;
}

interface ElementApi {
  /** The entity currently shown in the Element page (or null). */
  selected: ElementSelection | null;
  /** Select an entity and request navigation to the Element page. */
  openElement: (kind: EntityKind, id: string) => void;
  /** Bumped on every openElement call so the app can switch to the page. */
  navSeq: number;
}

const ElementContext = createContext<ElementApi>({
  selected: null,
  openElement: () => {},
  navSeq: 0,
});

export function ElementProvider({ children }: { children: ReactNode }) {
  const [selected, setSelected] = useState<ElementSelection | null>(null);
  const [navSeq, setNavSeq] = useState(0);

  const openElement = useCallback((kind: EntityKind, id: string) => {
    setSelected({ kind, id });
    setNavSeq((s) => s + 1);
  }, []);

  return (
    <ElementContext.Provider value={{ selected, openElement, navSeq }}>
      {children}
    </ElementContext.Provider>
  );
}

export function useElement(): ElementApi {
  return useContext(ElementContext);
}
