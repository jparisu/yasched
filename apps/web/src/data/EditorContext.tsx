/* eslint-disable react-refresh/only-export-components -- provider + hook colocated by design */
import { createContext, useContext, useState, ReactNode } from 'react';
import { EntityKind } from '../api/client';
import { EntityEditorDrawer } from '../components/editor/EntityEditorDrawer';
import { useData } from './DataContext';

interface EditorApi {
  openCreate: (kind: EntityKind) => void;
  openEdit: (kind: EntityKind, id: string) => void;
  canEdit: boolean;
  /** The kind currently open in the editor drawer, or null when it's closed. */
  activeKind: EntityKind | null;
}

const EditorContext = createContext<EditorApi>({
  openCreate: () => {},
  openEdit: () => {},
  canEdit: false,
  activeKind: null,
});

interface OpenState {
  kind: EntityKind;
  id: string | null;
}

export function EditorProvider({ children }: { children: ReactNode }) {
  const { readOnly, reload } = useData();
  const [state, setState] = useState<OpenState | null>(null);

  const api: EditorApi = {
    canEdit: !readOnly,
    activeKind: state?.kind ?? null,
    openCreate: (kind) => !readOnly && setState({ kind, id: null }),
    openEdit: (kind, id) => !readOnly && setState({ kind, id }),
  };

  return (
    <EditorContext.Provider value={api}>
      {children}
      {state && (
        <EntityEditorDrawer
          kind={state.kind}
          entityId={state.id}
          onClose={() => setState(null)}
          onSaved={reload}
        />
      )}
    </EditorContext.Provider>
  );
}

export function useEditor(): EditorApi {
  return useContext(EditorContext);
}
