import { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useData } from '../store';
import { useSettings } from '../settings';
import { ElementDTO } from '../types';
import { byType, isCancelled, whenOf } from '../lib/elements';
import { ElementView } from '../ui/ElementView';
import { addDays, fmtTime, isoDate, monthName, startOfWeek, today } from '../lib/format';
import { usePersistentState } from '../lib/usePersistentState';

// Paper-agenda: Mon–Wed on the left page, Thu–Sun on the right (weekend split).
export function Agenda({ onOpen }: { onOpen: (id: string) => void }) {
  const { elements } = useData();
  const { settings } = useSettings();
  const [cursor, setCursor] = useState<Date>(() => today());
  const [size, setSize] = usePersistentState<'fixed' | 'flexible'>('agenda-size', 'flexible');
  const start = startOfWeek(cursor, settings.weekStartsOnMonday);
  const days = Array.from({ length: 7 }, (_, i) => addDays(start, i));

  const byDay = useMemo(() => {
    const map: Record<string, ElementDTO[]> = {};
    for (const e of byType(elements, 'event')) {
      if (isCancelled(e)) continue;
      const w = whenOf(e);
      if (!w) continue;
      (map[isoDate(w)] ||= []).push(e);
    }
    return map;
  }, [elements]);

  const left = days.slice(0, 3);
  const right = days.slice(3);

  const fit = size === 'fixed';
  // Fit mode: each page is 3 equal rows so days share the height evenly.
  const colClass = fit ? 'grid grid-rows-3 gap-3 min-h-0 h-full' : 'space-y-3';
  const cellClass = fit ? 'min-h-0 overflow-y-auto' : '';

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-1">
        <button onClick={() => setCursor(addDays(cursor, -7))} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
          <ChevronLeft size={18} />
        </button>
        <button onClick={() => setCursor(today())} className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-sm">
          This week
        </button>
        <button onClick={() => setCursor(addDays(cursor, 7))} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
          <ChevronRight size={18} />
        </button>
        <h2 className="ml-2 font-semibold text-slate-700 dark:text-slate-200 flex-1">
          {monthName(start.getMonth())} {start.getDate()} – {monthName(days[6].getMonth())} {days[6].getDate()}
        </h2>
        <button
          onClick={() => setSize(size === 'fixed' ? 'flexible' : 'fixed')}
          title="Toggle agenda height"
          className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-sm"
        >
          {size === 'fixed' ? 'Fit screen' : 'Flexible'}
        </button>
      </div>

      <div
        className={`agenda-page agenda-fold rounded-2xl p-4 grid grid-cols-1 md:grid-cols-2 gap-6 ${
          fit ? 'md:h-[calc(100vh-11rem)] md:overflow-hidden' : ''
        }`}
      >
        {/* Left page: Mon–Wed (3 equal rows when fitting the screen) */}
        <div className={`min-w-0 ${colClass}`}>
          {left.map((d) => (
            <div key={isoDate(d)} className={cellClass}>
              <DayBlock date={d} items={byDay[isoDate(d)] ?? []} onOpen={onOpen} />
            </div>
          ))}
        </div>
        {/* Right page: Thu, Fri, then Sat + Sun side by side (also 3 rows) */}
        <div className={`min-w-0 ${colClass}`}>
          {right.slice(0, 2).map((d) => (
            <div key={isoDate(d)} className={cellClass}>
              <DayBlock date={d} items={byDay[isoDate(d)] ?? []} onOpen={onOpen} />
            </div>
          ))}
          <div className={`grid grid-cols-2 gap-3 ${cellClass}`}>
            {right.slice(2).map((d) => (
              <DayBlock key={isoDate(d)} date={d} items={byDay[isoDate(d)] ?? []} onOpen={onOpen} compact />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function DayBlock({
  date,
  items,
  onOpen,
  compact,
}: {
  date: Date;
  items: ElementDTO[];
  onOpen: (id: string) => void;
  compact?: boolean;
}) {
  return (
    <div>
      <div className="flex items-baseline gap-2 border-b border-amber-900/10 dark:border-white/10 pb-1 mb-2">
        <span className={`font-bold ${compact ? 'text-lg' : 'text-2xl'} text-slate-700 dark:text-slate-200`}>
          {date.getDate()}
        </span>
        <span className="text-xs text-slate-500">
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][(date.getDay() + 6) % 7]}
        </span>
      </div>
      <div className="space-y-1">
        {items.length === 0 && <p className="text-xs text-slate-400">—</p>}
        {items.map((e) => {
          const w = whenOf(e);
          return (
            <ElementView
              key={e.id}
              element={e}
              mode="line"
              onClick={onOpen}
              extra={w ? fmtTime(w) : undefined}
            />
          );
        })}
      </div>
    </div>
  );
}
