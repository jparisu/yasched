import { useRef } from 'react';
import { ItemStyle, CardShape, DisplayStyle } from '../../types';
import { Clock, AlertCircle, RefreshCw, CheckCircle2, CornerDownRight } from 'lucide-react';
import { tintRgba } from '../../lib/colors';
import { levelOf } from '../../lib/levels';
import { useSettings } from '../../data/SettingsContext';

interface DisplayItemProps {
  title: string;
  description?: string;
  displayStyle: DisplayStyle;
  itemStyle?: ItemStyle;
  /** Accepted for call-site convenience; styling is derived from itemStyle. */
  topicId?: string;
  startTime?: string;
  endTime?: string;
  priority?: number;
  status?: 'todo' | 'doing' | 'done';
  recurring?: boolean;
  deadline?: Date;
  onClick?: () => void;
  onDoubleClick?: () => void;
  /** Nesting depth for subtasks — indents the item to show hierarchy. */
  depth?: number;
  /** Extra classes for the root button (e.g. `h-full` to fill a time slot). */
  className?: string;
}

const getShapeClass = (shape: CardShape): string => {
  switch (shape) {
    case 'rectangle': return 'rounded-none';
    case 'rounded': return 'rounded-xl';
    case 'curvy': return 'rounded-2xl';
    case 'cloudy': return 'cloudy-shape';
    case 'sticky': return 'sticky-shape';
    default: return 'rounded-xl';
  }
};

const DEFAULT_ACCENT = '#94a3b8';

const PRIORITY_PILL: Record<'low' | 'medium' | 'high', string> = {
  high: 'bg-rose-100 text-rose-600 dark:bg-rose-900/40 dark:text-rose-300',
  medium: 'bg-peach-100 text-peach-600 dark:bg-peach-900/40 dark:text-peach-300',
  low: 'bg-mint-100 text-mint-600 dark:bg-mint-900/40 dark:text-mint-300',
};

export function DisplayItem({
  title,
  description,
  displayStyle,
  itemStyle,
  startTime,
  endTime,
  priority,
  status,
  recurring,
  deadline,
  onClick,
  onDoubleClick,
  depth = 0,
  className = '',
}: DisplayItemProps) {
  const { settings } = useSettings();
  const priorityLevel = levelOf(priority, settings.priorityRanges);
  const accent = itemStyle?.leftColor || DEFAULT_ACCENT;
  const dot = itemStyle?.dotColor || accent;
  const shape: CardShape = itemStyle?.shape || 'rounded';
  const surface = { backgroundColor: tintRgba(accent, 0.16), borderLeftColor: accent };
  const indent = depth > 0 ? { marginLeft: depth * 16 } : {};
  const rootStyle = { ...surface, ...indent };
  const subMark =
    depth > 0 ? (
      <CornerDownRight size={12} className="text-slate-400 flex-shrink-0" />
    ) : null;

  // Distinguish single- from double-click: defer the single-click briefly so a
  // double-click (open Element panel) doesn't also fire the single-click (open
  // the editor drawer) on top of it.
  const clickTimer = useRef<number | null>(null);
  const handleClick = () => {
    if (!onClick) return;
    if (!onDoubleClick) return onClick();
    if (clickTimer.current) window.clearTimeout(clickTimer.current);
    clickTimer.current = window.setTimeout(() => {
      clickTimer.current = null;
      onClick();
    }, 220);
  };
  const handleDoubleClick = () => {
    if (clickTimer.current) {
      window.clearTimeout(clickTimer.current);
      clickTimer.current = null;
    }
    onDoubleClick?.();
  };

  // Hover tooltip: name plus the start/end time when available.
  const timeText = startTime ? `${startTime}${endTime ? `–${endTime}` : ''}` : '';
  const hoverTitle = timeText ? `${title} · ${timeText}` : title;

  const deadlineText = deadline
    ? Math.ceil((new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    : null;

  if (displayStyle === 'collapsed') {
    return (
      <button
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
        title={hoverTitle}
        className={`flex items-center gap-1.5 px-2 py-1 border-l-[3px] ${getShapeClass(shape)} transition-all hover:scale-105 ${className}`}
        style={rootStyle}
      >
        {subMark}
        <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: dot }} />
        <span className="text-sm text-slate-700 dark:text-slate-200 truncate">{title}</span>
        {status === 'done' && <CheckCircle2 size={12} className="text-mint-500 ml-auto" />}
      </button>
    );
  }

  if (displayStyle === 'line') {
    return (
      <button
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
        title={hoverTitle}
        className={`w-full flex items-center gap-2 px-3 py-1.5 border-l-4 ${getShapeClass(shape)} transition-all hover:shadow-md ${className}`}
        style={rootStyle}
      >
        {subMark}
        <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: dot }} />
        {/* title + inline secondary info, all on one line */}
        <span className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate min-w-0">{title}</span>
        {startTime && (
          <span className="text-xs text-slate-500 dark:text-slate-400 whitespace-nowrap flex-shrink-0">
            {startTime}{endTime && `–${endTime}`}
          </span>
        )}
        <span className="flex-1" />
        {priorityLevel && (
          <span
            title={`priority ${priority} (${priorityLevel})`}
            className={`text-xs px-1.5 py-0.5 rounded flex-shrink-0 ${PRIORITY_PILL[priorityLevel]}`}
          >
            P{priority}
          </span>
        )}
        {status === 'done' && <CheckCircle2 size={14} className="text-mint-500 flex-shrink-0" />}
        {recurring && <RefreshCw size={12} className="text-slate-400 flex-shrink-0" />}
        {deadlineText !== null && deadlineText <= 3 && (
          <span className="text-xs text-rose-500 flex items-center gap-0.5 flex-shrink-0">
            <AlertCircle size={10} />
            {deadlineText <= 0 ? '!' : `${deadlineText}d`}
          </span>
        )}
      </button>
    );
  }

  return (
    <button
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      title={hoverTitle}
      className={`w-full text-left p-3 border-l-4 ${getShapeClass(shape)} transition-all hover:shadow-lg ${
        shape === 'sticky' ? 'sticky-note' : ''
      } ${className}`}
      style={rootStyle}
    >
      <div className="flex items-start gap-2">
        {subMark}
        <span className="w-3 h-3 rounded-full mt-0.5 flex-shrink-0" style={{ backgroundColor: dot }} />
        <div className="flex-1 min-w-0">
          <p className="font-medium text-slate-800 dark:text-slate-100">{title}</p>
          {description && (
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">{description}</p>
          )}
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            {startTime && (
              <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
                <Clock size={10} />
                {startTime}{endTime && ` - ${endTime}`}
              </span>
            )}
            {priorityLevel && (
              <span
                title={`priority ${priority} (${priorityLevel})`}
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${PRIORITY_PILL[priorityLevel]}`}
              >
                priority {priority}
              </span>
            )}
            {recurring && (
              <span className="text-xs text-slate-400 flex items-center gap-0.5">
                <RefreshCw size={10} />
                repeats
              </span>
            )}
            {status === 'done' && (
              <span className="text-xs text-mint-500 flex items-center gap-0.5">
                <CheckCircle2 size={12} />
                done
              </span>
            )}
          </div>
        </div>
      </div>
      {deadlineText !== null && deadlineText <= 3 && (
        <div className="mt-2 pt-2 border-t border-slate-300/30 dark:border-slate-600/40 text-xs text-rose-600 dark:text-rose-400 flex items-center gap-1">
          <AlertCircle size={12} />
          {deadlineText <= 0 ? 'Overdue' : `${deadlineText} day${deadlineText > 1 ? 's' : ''} left`}
        </div>
      )}
    </button>
  );
}
