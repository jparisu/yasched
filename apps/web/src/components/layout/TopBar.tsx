import { Moon, Sun } from 'lucide-react';
import { ViewMode, Settings } from '../../types';

interface TopBarProps {
  currentView: ViewMode;
  settings: Settings;
  onThemeToggle: () => void;
}

const viewTitles: Record<ViewMode, string> = {
  statistics: 'Statistics',
  agenda: 'Agenda',
  calendar: 'Calendar',
  taskboard: 'Task Board',
  focus: 'Focus',
  graph: 'Database Graph',
  settings: 'Settings',
};

const viewColors: Record<ViewMode, string> = {
  statistics: 'from-sky-500 to-lavender-500',
  agenda: 'from-peach-500 to-lemon-500',
  calendar: 'from-mint-500 to-teal-500',
  taskboard: 'from-lavender-500 to-rose-500',
  focus: 'from-teal-500 to-sky-500',
  graph: 'from-rose-500 to-coral-500',
  settings: 'from-slate-500 to-slate-600',
};

export function TopBar({ currentView, onThemeToggle }: TopBarProps) {
  const isDark = localStorage.getItem('theme') === 'dark';
  const gradient = viewColors[currentView];

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
