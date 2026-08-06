import { useCallback, useEffect, useReducer, useState } from 'react';
import { ElementType, PanelId } from '../types';
import { useData } from '../store';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { ElementDrawer } from '../ui/ElementDrawer';
import { Main } from '../panels/Main';
import { Stats } from '../panels/Stats';
import { Focus } from '../panels/Focus';
import { Attributes } from '../panels/Attributes';
import { SettingsPanel } from '../panels/SettingsPanel';
import { TopicGraph } from '../panels/TopicGraph';
import { Calendar } from '../panels/Calendar';
import { Agenda } from '../panels/Agenda';
import { Timeline } from '../panels/Timeline';
import { Taskboard } from '../panels/Taskboard';
import { Timeboard } from '../panels/Timeboard';
import { Effort } from '../panels/Effort';
import { ElementManagement } from '../panels/ElementManagement';

const PANELS: PanelId[] = [
  'main', 'stats', 'focus', 'attributes', 'settings',
  'topic-graph', 'topic-manage',
  'calendar', 'agenda', 'timeline', 'event-manage',
  'timeboard', 'effort', 'schedule-manage',
  'taskboard', 'task-manage',
];

const MANAGE_PANEL: Record<ElementType, PanelId> = {
  topic: 'topic-manage',
  event: 'event-manage',
  task: 'task-manage',
  schedule: 'schedule-manage',
};

// --- Navigation history (a back/forward stack, VSCode-style) ----------------

interface NavEntry {
  panel: PanelId;
  select?: string; // preselected element for a management panel
}
interface NavState {
  stack: NavEntry[];
  index: number;
}
type NavAction =
  | { type: 'go'; entry: NavEntry }
  | { type: 'back' }
  | { type: 'forward' };

function navReducer(state: NavState, action: NavAction): NavState {
  switch (action.type) {
    case 'go': {
      const base = state.stack.slice(0, state.index + 1);
      const last = base[base.length - 1];
      if (last && last.panel === action.entry.panel && last.select === action.entry.select) {
        return state; // no-op: already here
      }
      return { stack: [...base, action.entry], index: base.length };
    }
    case 'back':
      return state.index > 0 ? { ...state, index: state.index - 1 } : state;
    case 'forward':
      return state.index < state.stack.length - 1 ? { ...state, index: state.index + 1 } : state;
  }
}

function initialNav(): NavState {
  const saved = localStorage.getItem('yasched-panel') as PanelId | null;
  const panel = saved && PANELS.includes(saved) ? saved : 'main';
  return { stack: [{ panel }], index: 0 };
}

export function App() {
  const { loading, error, reload, byId } = useData();
  const [nav, dispatch] = useReducer(navReducer, undefined, initialNav);
  const [openId, setOpenId] = useState<string | null>(null);

  const current = nav.stack[nav.index];
  const panel = current.panel;
  const pendingSelect = current.select;

  useEffect(() => {
    localStorage.setItem('yasched-panel', panel);
  }, [panel]);

  // Esc closes the element drawer.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpenId(null);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [setOpenId]);

  const onOpen = useCallback((id: string) => setOpenId(id), [setOpenId]);
  const setPanel = useCallback((p: PanelId) => dispatch({ type: 'go', entry: { panel: p } }), []);

  const goToElement = useCallback(
    (id: string) => {
      const el = byId[id];
      if (!el) return;
      setOpenId(null);
      dispatch({ type: 'go', entry: { panel: MANAGE_PANEL[el.type], select: id } });
    },
    [byId, setOpenId],
  );

  const renderPanel = () => {
    switch (panel) {
      case 'main': return <Main onOpen={onOpen} />;
      case 'stats': return <Stats onOpen={onOpen} />;
      case 'focus': return <Focus onOpen={onOpen} />;
      case 'attributes': return <Attributes />;
      case 'settings': return <SettingsPanel />;
      case 'topic-graph': return <TopicGraph onOpen={onOpen} />;
      case 'topic-manage': return <ElementManagement type="topic" pendingId={pendingSelect} />;
      case 'calendar': return <Calendar onOpen={onOpen} />;
      case 'agenda': return <Agenda onOpen={onOpen} />;
      case 'timeline': return <Timeline onOpen={onOpen} />;
      case 'event-manage': return <ElementManagement type="event" pendingId={pendingSelect} />;
      case 'timeboard': return <Timeboard onOpen={onOpen} />;
      case 'effort': return <Effort onOpen={onOpen} />;
      case 'schedule-manage': return <ElementManagement type="schedule" pendingId={pendingSelect} />;
      case 'taskboard': return <Taskboard onOpen={onOpen} />;
      case 'task-manage': return <ElementManagement type="task" pendingId={pendingSelect} />;
      default: return <Main onOpen={onOpen} />;
    }
  };

  return (
    <div className="min-h-screen">
      <div className="app-bg min-h-screen">
        <Sidebar current={panel} onChange={setPanel} />
        <div className="ml-16 min-h-screen">
          <TopBar
            current={panel}
            onBack={() => dispatch({ type: 'back' })}
            onForward={() => dispatch({ type: 'forward' })}
            canBack={nav.index > 0}
            canForward={nav.index < nav.stack.length - 1}
          />
          <main className="p-4 md:p-6">
            {error ? (
              <div className="flex flex-col items-center justify-center h-[60vh] gap-4 text-center">
                <p className="text-lg font-semibold text-rose-600 dark:text-rose-400">
                  Could not load your database
                </p>
                <p className="text-sm text-slate-500 max-w-md">{error}</p>
                <button onClick={reload} className="px-4 py-2 rounded-lg bg-sky-500 text-white text-sm">
                  Retry
                </button>
              </div>
            ) : loading ? (
              <div className="flex items-center justify-center h-[60vh] text-slate-400">Loading…</div>
            ) : (
              renderPanel()
            )}
          </main>
        </div>
      </div>
      {openId && (
        <ElementDrawer
          elementId={openId}
          onClose={() => setOpenId(null)}
          onOpen={setOpenId}
          onConfigure={goToElement}
        />
      )}
    </div>
  );
}
