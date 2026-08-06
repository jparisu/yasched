import { useMemo, useState } from 'react';
import { useData } from '../store';
import { ElementDTO } from '../types';
import { byType, byWhenAsc, displayName, isCancelled, whenOf } from '../lib/elements';
import { backgroundStyle } from '../lib/layout';
import { ElementView } from '../ui/ElementView';
import { fmtDate, monthName } from '../lib/format';
import { usePersistentState } from '../lib/usePersistentState';

type Orientation = 'horizontal' | 'vertical';

// A single-axis view of events (the calendar condensed onto one line).
export function Timeline({ onOpen }: { onOpen: (id: string) => void }) {
  const { elements } = useData();
  const [orientation, setOrientation] = usePersistentState<Orientation>('timeline-orientation', 'horizontal');

  const events = useMemo(
    () =>
      byType(elements, 'event')
        .filter((e) => !isCancelled(e) && whenOf(e) != null)
        .sort(byWhenAsc),
    [elements],
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">{events.length} events</p>
        <div className="flex gap-2">
          {(['horizontal', 'vertical'] as const).map((o) => (
            <button
              key={o}
              onClick={() => setOrientation(o)}
              className={`px-3 py-1.5 rounded-lg border text-sm capitalize ${
                orientation === o
                  ? 'bg-sky-500 text-white border-sky-500'
                  : 'border-slate-200 dark:border-slate-700'
              }`}
            >
              {o}
            </button>
          ))}
        </div>
      </div>

      {events.length === 0 ? (
        <div className="card p-8 text-center text-slate-400">No dated events.</div>
      ) : orientation === 'horizontal' ? (
        <HorizontalAxis events={events} onOpen={onOpen} />
      ) : (
        <div className="card p-4 space-y-1.5">
          {events.map((e) => (
            <ElementView key={e.id} element={e} mode="line" onClick={onOpen} when="datetime" />
          ))}
        </div>
      )}
    </div>
  );
}

function fmtSpan(hours: number): string {
  if (hours < 48) return `${Math.max(1, Math.round(hours))}h`;
  const days = hours / 24;
  if (days < 60) return `${Math.round(days)}d`;
  return `${Math.round(days / 30)}mo`;
}

function HorizontalAxis({ events, onOpen }: { events: ElementDTO[]; onOpen: (id: string) => void }) {
  const [zoom, setZoom] = usePersistentState<number>('timeline-zoom', 0);
  const [hover, setHover] = useState<string | null>(null);

  const times = events.map((e) => whenOf(e)!.getTime());
  const min = Math.min(...times);
  const max = Math.max(...times);
  const span = Math.max(max - min, 1);
  const pos = (t: number) => ((t - min) / span) * 100;

  // Zoom: 0 = show ALL (100% width), 1 = ~1h visible (log-scaled width).
  const spanHours = span / 3_600_000;
  const base = Math.min(Math.max(spanHours, 1), 500);
  const widthPct = Math.min(8000, 100 * Math.pow(base, zoom));
  const visibleHours = spanHours / (widthPct / 100);

  // Month gridlines across the span.
  const ticks: { left: number; label: string }[] = [];
  const cursor = new Date(new Date(min).getFullYear(), new Date(min).getMonth(), 1);
  const end = new Date(max);
  while (cursor <= end) {
    ticks.push({ left: pos(cursor.getTime()), label: `${monthName(cursor.getMonth())} ${cursor.getFullYear()}` });
    cursor.setMonth(cursor.getMonth() + 1);
  }

  return (
    <div className="card p-4 space-y-3">
      <div className="flex items-center gap-3">
        <span className="text-xs text-slate-400">All</span>
        <input
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={zoom}
          onChange={(e) => setZoom(Number(e.target.value))}
          className="flex-1 accent-sky-500"
          title="Zoom the timeline (log scale, ALL → 1h)"
        />
        <span className="text-xs text-slate-400">1h</span>
        <span className="text-xs text-slate-500 w-24 text-right">shows ~{fmtSpan(visibleHours)}</span>
      </div>

      <div className="overflow-x-auto">
        <div className="relative" style={{ width: `${widthPct}%`, minWidth: '100%', height: 150 }}>
          {ticks.map((t, i) => (
            <div
              key={i}
              className="absolute top-0 bottom-6 border-l border-slate-200/70 dark:border-slate-700"
              style={{ left: `${t.left}%` }}
            >
              <span className="absolute -top-1 left-1 text-[10px] text-slate-400 whitespace-nowrap">{t.label}</span>
            </div>
          ))}
          <div className="absolute left-0 right-0 h-0.5 bg-slate-300 dark:bg-slate-600" style={{ top: 78 }} />

          {events.map((e, i) => {
            const t = whenOf(e)!.getTime();
            const above = i % 2 === 0;
            const isHover = hover === e.id;
            return (
              <div
                key={e.id}
                className="absolute -translate-x-1/2 flex flex-col items-center cursor-pointer group"
                style={{ left: `${pos(t)}%`, top: above ? 30 : 86, zIndex: isHover ? 20 : undefined }}
                onClick={() => onOpen(e.id)}
                onMouseEnter={() => setHover(e.id)}
                onMouseLeave={() => setHover((h) => (h === e.id ? null : h))}
              >
                {!above && <div className="w-px h-4 bg-slate-300 dark:bg-slate-600" />}
                <div
                  className="w-3 h-3 rounded-full border border-slate-400 group-hover:scale-125 transition-transform"
                  style={backgroundStyle(e.layout)}
                />
                <span className="mt-0.5 text-[10px] text-slate-500 dark:text-slate-300 max-w-[90px] truncate">
                  {displayName(e)}
                </span>
                {above && <div className="w-px h-4 bg-slate-300 dark:bg-slate-600" />}

                {/* 16.1 — hover card */}
                {isHover && (
                  <div
                    className="absolute z-30 w-48 pointer-events-none"
                    style={{
                      left: '50%',
                      transform: 'translateX(-50%)',
                      ...(above ? { top: '100%' } : { bottom: '100%' }),
                    }}
                  >
                    <div className="my-1">
                      <ElementView element={e} mode="card" extra={fmtDate(whenOf(e)!)} />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
