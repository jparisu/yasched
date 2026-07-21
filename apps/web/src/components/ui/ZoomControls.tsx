import { ZoomIn, ZoomOut, Maximize } from 'lucide-react';

interface ZoomControlsProps {
  zoom: number;
  onStep: (dir: 1 | -1) => void;
  onReset: () => void;
}

/** Compact − / percentage / + control to scale a panel's content. */
export function ZoomControls({ zoom, onStep, onReset }: ZoomControlsProps) {
  const btn = 'p-1.5 rounded-md text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-white dark:hover:bg-slate-700 transition-colors';
  return (
    <div className="flex items-center gap-1 p-0.5 bg-slate-100 dark:bg-slate-800 rounded-lg">
      <span className="text-xs font-medium text-slate-500 dark:text-slate-400 pl-1.5">Zoom:</span>
      <button onClick={() => onStep(-1)} className={btn} title="Smaller">
        <ZoomOut size={16} />
      </button>
      <button onClick={onReset} className="text-xs font-medium text-slate-600 dark:text-slate-300 w-10 text-center tabular-nums" title="Reset zoom">
        {Math.round(zoom * 100)}%
      </button>
      <button onClick={() => onStep(1)} className={btn} title="Bigger">
        <ZoomIn size={16} />
      </button>
      <button onClick={onReset} className={btn} title="Fit / reset">
        <Maximize size={14} />
      </button>
    </div>
  );
}
