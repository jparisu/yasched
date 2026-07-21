/* eslint-disable react-refresh/only-export-components -- provider + hook colocated by design */
import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { HelpModal } from './HelpModal';
import { DEFAULT_PAGE_ID } from './helpContent';

interface HelpApi {
  /** Open the manual, optionally jumping to a specific page id. */
  openHelp: (pageId?: string) => void;
  closeHelp: () => void;
  isOpen: boolean;
}

const HelpContext = createContext<HelpApi>({
  openHelp: () => {},
  closeHelp: () => {},
  isOpen: false,
});

export function HelpProvider({ children }: { children: ReactNode }) {
  const [pageId, setPageId] = useState<string | null>(null);

  const openHelp = useCallback((id?: string) => setPageId(id ?? DEFAULT_PAGE_ID), []);
  const closeHelp = useCallback(() => setPageId(null), []);

  return (
    <HelpContext.Provider value={{ openHelp, closeHelp, isOpen: pageId !== null }}>
      {children}
      {pageId !== null && (
        <HelpModal activePageId={pageId} onNavigate={setPageId} onClose={closeHelp} />
      )}
    </HelpContext.Provider>
  );
}

export function useHelp(): HelpApi {
  return useContext(HelpContext);
}
