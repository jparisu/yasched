import { ArrowLeft, ArrowRight, Moon, RefreshCw, Sun } from 'lucide-react';
import { PanelId } from '../types';
import { NAV } from './nav';
import { useSettings } from '../settings';
import { useData } from '../store';

const MANAGE_TITLE: Partial<Record<PanelId, string>> = {
  'topic-manage': 'Topic Configuration',
  'event-manage': 'Event Configuration',
  'task-manage': 'Task Configuration',
  'schedule-manage': 'Schedule Configuration',
};

interface Props {
  current: PanelId;
  onBack: () => void;
  onForward: () => void;
  canBack: boolean;
  canForward: boolean;
}

export function TopBar({ current, onBack, onForward, canBack, canForward }: Props) {
  const { settings, updateSetting } = useSettings();
  const { reload, validation } = useData();
  const title = MANAGE_TITLE[current] ?? NAV.find((n) => n.id === current)?.label ?? 'yasched';
  const errors = validation?.errorCount ?? 0;
  const warnings = validation?.warningCount ?? 0;

  const iconBtn =
    'p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 disabled:opacity-30 disabled:hover:bg-transparent';

  return (
    <header className="sticky top-0 z-30 backdrop-blur bg-white/70 dark:bg-slate-900/70 border-b border-slate-200/60 dark:border-slate-800 px-4 md:px-6 py-3 flex items-center justify-between gap-3">
      <div className="flex items-center gap-1">
        <button onClick={onBack} disabled={!canBack} title="Back" className={iconBtn}>
          <ArrowLeft size={18} />
        </button>
        <button onClick={onForward} disabled={!canForward} title="Forward" className={iconBtn}>
          <ArrowRight size={18} />
        </button>
        <h1 className="ml-2 text-lg font-bold text-slate-800 dark:text-slate-100">{title}</h1>
      </div>
      <div className="flex items-center gap-2">
        {errors > 0 && (
          <span className="text-xs px-2 py-1 rounded-full bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300">
            {errors} error{errors > 1 ? 's' : ''}
          </span>
        )}
        {warnings > 0 && (
          <span className="text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
            {warnings} warning{warnings > 1 ? 's' : ''}
          </span>
        )}
        <button onClick={reload} title="Reload database from disk" className={iconBtn}>
          <RefreshCw size={18} />
        </button>
        <button
          onClick={() => updateSetting('theme', settings.theme === 'dark' ? 'light' : 'dark')}
          title={settings.theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
          className={iconBtn}
        >
          {settings.theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
