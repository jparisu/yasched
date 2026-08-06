import { CSSProperties } from 'react';
import { ElementDTO } from '../types';
import { accentStyle, cardStyle, iconValue, pinColor, textOn } from '../lib/layout';
import { attrString, categoryLabel, displayName, isCancelled, whenOf } from '../lib/elements';
import { fmtDateTime, fmtTime, hasTime } from '../lib/format';
import { ElementViewMode } from '../settings';

type WhenMode = 'datetime' | 'time' | 'none';

interface ElementViewProps {
  element: ElementDTO;
  mode?: ElementViewMode;
  onClick?: (id: string) => void;
  /** Panel-specific extra text shown on the line. */
  extra?: string;
  /** Which timing to surface on the line (default: time if the element has one). */
  when?: WhenMode;
}

const TYPE_BADGE: Record<string, string> = {
  topic: 'T',
  event: 'E',
  task: '✓',
  schedule: '↻',
};

function rawWhen(element: ElementDTO): string | undefined {
  return attrString(element, element.type === 'task' ? 'deadline' : 'start');
}

/** Small uppercase category tag: deadline / reminder for auto-events, else auto. */
function badgeText(element: ElementDTO): string | null {
  const cat = categoryLabel(element);
  if (cat === 'deadline' || cat === 'reminder') return cat;
  return element.virtual ? 'auto' : null;
}

function whenText(element: ElementDTO, mode: WhenMode): string {
  if (mode === 'none') return '';
  const raw = rawWhen(element);
  const d = whenOf(element);
  if (!d) return '';
  if (mode === 'datetime') return fmtDateTime(raw);
  return hasTime(raw) ? fmtTime(d) : ''; // 'time'
}

export function ElementView({ element, mode = 'card', onClick, extra, when = 'time' }: ElementViewProps) {
  const name = displayName(element);
  const cancelled = isCancelled(element);
  const icon = iconValue(element.layout);
  const pin = pinColor(element.layout);
  const badge = badgeText(element);
  const textColor = textOn(element.layout);

  const commonClass = `cursor-pointer transition-transform hover:scale-[1.01] ${
    cancelled ? 'line-through opacity-50' : ''
  } ${element.virtual ? 'border-dashed' : ''}`;

  if (mode === 'point') {
    const style: CSSProperties = { ...accentStyle(element.layout), width: 14, height: 14 };
    return (
      <span
        title={name}
        onClick={() => onClick?.(element.id)}
        className={`inline-block rounded-full border border-slate-300 ${commonClass}`}
        style={style}
      />
    );
  }

  if (mode === 'line') {
    const timing = whenText(element, when);
    return (
      <div
        onClick={() => onClick?.(element.id)}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200/60 dark:border-slate-700 ${commonClass}`}
        style={{ ...accentStyle(element.layout), color: textColor }}
      >
        {pin && <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: pin }} />}
        {icon && <span className="flex-shrink-0">{icon}</span>}
        <span className="truncate text-sm font-medium flex-1">{name}</span>
        {extra && <span className="text-xs opacity-70">{extra}</span>}
        {timing && <span className="text-xs font-medium tabular-nums opacity-90">{timing}</span>}
        {badge && (
          <span className="text-[10px] uppercase tracking-wide opacity-60 flex-shrink-0">{badge}</span>
        )}
      </div>
    );
  }

  // card
  const style = cardStyle(element.layout);
  return (
    <div
      onClick={() => onClick?.(element.id)}
      className={`relative rounded-2xl border border-slate-200/60 dark:border-slate-700 p-3 shadow-sm ${commonClass}`}
      style={{ ...style, color: style.color ?? textColor }}
    >
      <div className="flex items-start gap-2">
        <span className="text-lg leading-none flex-shrink-0">{icon ?? TYPE_BADGE[element.type]}</span>
        <div className="min-w-0 flex-1">
          <div className="font-semibold truncate">{name}</div>
          {whenOf(element) && <div className="text-xs opacity-80">{fmtDateTime(rawWhen(element))}</div>}
          {extra && <div className="text-xs opacity-70">{extra}</div>}
        </div>
        {pin && <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: pin }} />}
      </div>
      {badge && (
        <span className="absolute top-1 right-2 text-[10px] uppercase tracking-wide opacity-70">{badge}</span>
      )}
    </div>
  );
}
