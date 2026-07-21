import { useState } from 'react';
import { Moon, Sun, Plus, ListTodo, CalendarPlus, FolderPlus, HelpCircle } from 'lucide-react';
import { ViewMode, Settings } from '../../types';
import { useEditor } from '../../data/EditorContext';
import { EntityKind } from '../../api/client';
import { useHelp, VIEW_TO_PAGE, KIND_TO_PAGE } from '../../help';

interface TopBarProps {
  currentView: ViewMode;
  settings: Settings;
  onThemeToggle: () => void;
}

const viewTitles: Record<ViewMode, string> = {
  statistics: 'Dashboard',
  agenda: 'Agenda',
  calendar: 'Calendar',
  weekly: 'Weekly View',
  taskboard: 'Task Board',
  focus: 'Focus',
  graph: 'Database Graph',
  element: 'Element',
  settings: 'Settings',
};

// Each pair spans two clearly different hues so the gradient reads as a gradient.
const viewColors: Record<ViewMode, string> = {
  statistics: 'from-sky-500 to-lavender-500',
  agenda: 'from-peach-500 to-rose-500',
  calendar: 'from-mint-500 to-sky-500',
  weekly: 'from-teal-500 to-lavender-500',
  taskboard: 'from-lavender-500 to-rose-500',
  focus: 'from-teal-500 to-sky-500',
  graph: 'from-rose-500 to-lemon-500',
  element: 'from-rose-500 to-sky-500',
  settings: 'from-slate-400 to-slate-600',
};

const NEW_OPTIONS: { kind: EntityKind; label: string; icon: React.ReactNode }[] = [
  { kind: 'tasks', label: 'Task', icon: <ListTodo size={15} /> },
  { kind: 'events', label: 'Event', icon: <CalendarPlus size={15} /> },
  { kind: 'topics', label: 'Topic', icon: <FolderPlus size={15} /> },
];

export function TopBar({ currentView, onThemeToggle }: TopBarProps) {
  const isDark = localStorage.getItem('theme') === 'dark';
  const gradient = viewColors[currentView];
  const { openCreate, canEdit, activeKind } = useEditor();
  const { openHelp } = useHelp();
  const [menuOpen, setMenuOpen] = useState(false);

  // Context-aware help: if the element editor is open, jump to that element's
  // page; otherwise open the page for the current panel.
  const handleHelp = () =>
    openHelp(activeKind ? KIND_TO_PAGE[activeKind] : VIEW_TO_PAGE[currentView]);

  return (
    <header className="sticky top-0 z-30 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200/50 dark:border-slate-800">
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center text-white shadow-md`}>
            <span className="text-lg font-bold">{viewTitles[currentView][0]}</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-800 dark:text-slate-100">
              {viewTitles[currentView]}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {canEdit && (
            <div className="relative">
              <button
                onClick={() => setMenuOpen((v) => !v)}
                onBlur={() => setTimeout(() => setMenuOpen(false), 150)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-semibold bg-gradient-to-br from-sky-500 to-lavender-500 text-white shadow-md hover:shadow-lg"
              >
                <Plus size={16} /> New
              </button>
              {menuOpen && (
                <div className="absolute right-0 mt-1 w-40 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-lg py-1 z-40">
                  {NEW_OPTIONS.map((o) => (
                    <button
                      key={o.kind}
                      onClick={() => {
                        setMenuOpen(false);
                        openCreate(o.kind);
                      }}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700"
                    >
                      {o.icon} New {o.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
          <button
            onClick={handleHelp}
            title="Open the manual"
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-semibold text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          >
            <HelpCircle size={16} /> Help
          </button>
          <button
            onClick={onThemeToggle}
            className={`p-2.5 rounded-xl transition-all ${
              isDark
                ? 'bg-gradient-to-br from-lemon-400 to-peach-400 text-slate-900'
                : 'bg-gradient-to-br from-lavender-500 to-sky-500 text-white'
            } shadow-md hover:shadow-lg`}
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </div>
    </header>
  );
}
