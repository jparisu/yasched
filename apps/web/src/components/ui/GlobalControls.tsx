import { DisplayStyle } from '../../types';
import { LayoutGrid, AlignLeft, Minimize2 } from 'lucide-react';

interface GlobalControlsProps {
  displayStyle: DisplayStyle;
  onDisplayStyleChange: (style: DisplayStyle) => void;
}

// The one control every panel that lists elements shows: how items are drawn
// (square cards / lines / points). Item *shape* is a per-element layout option.
export function GlobalControls({ displayStyle, onDisplayStyleChange }: GlobalControlsProps) {
  const seg = (active: boolean) =>
    `p-1.5 rounded-md transition-all ${
      active
        ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
        : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200'
    }`;

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-medium text-slate-500 dark:text-slate-400">View:</span>
      <div className="flex items-center gap-0.5 p-0.5 bg-slate-100 dark:bg-slate-800 rounded-lg">
        <button onClick={() => onDisplayStyleChange('square')} className={seg(displayStyle === 'square')} title="Square (cards)">
          <LayoutGrid size={16} />
        </button>
        <button onClick={() => onDisplayStyleChange('line')} className={seg(displayStyle === 'line')} title="Line">
          <AlignLeft size={16} />
        </button>
        <button onClick={() => onDisplayStyleChange('collapsed')} className={seg(displayStyle === 'collapsed')} title="Point (collapsed)">
          <Minimize2 size={16} />
        </button>
      </div>
    </div>
  );
}
