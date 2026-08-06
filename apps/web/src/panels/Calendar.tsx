import { useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useData } from '../store';
import { useSettings } from '../settings';
import { ElementDTO } from '../types';
import { byType, isCancelled, whenOf } from '../lib/elements';
import { ElementView } from '../ui/ElementView';
import { addDays, isoDate, monthName, sameDay, startOfWeek, today, weekdayShort } from '../lib/format';

// TODO(v0.5): the spec asks for a day / week / month / year selector. Only
// month and week are implemented; `day` and `year` are deliberately deferred —
// the Timeline panel already covers most of what a day view would show, and a
// year view needs a denser element renderer than ElementView currently offers.
// Adding them means extending this union, `shift()`, and the render switch below.
type View = 'month' | 'week';

export function Calendar({ onOpen }: { onOpen: (id: string) => void }) {
  const { elements } = useData();
  const { settings } = useSettings();
  const [view, setView] = useState<View>('month');
  const [cursor, setCursor] = useState<Date>(() => today());

  const events = useMemo(
    () => byType(elements, 'event').filter((e) => !isCancelled(e) && whenOf(e) != null),
    [elements],
  );
  const byDay = useMemo(() => {
    const map: Record<string, ElementDTO[]> = {};
    for (const e of events) {
      const w = whenOf(e);
      if (!w) continue;
      const key = isoDate(w);
      (map[key] ||= []).push(e);
    }
    return map;
  }, [events]);

  const step = (dir: number) =>
    setCursor((c) => (view === 'month' ? new Date(c.getFullYear(), c.getMonth() + dir, 1) : addDays(c, dir * 7)));

  const title =
    view === 'month'
      ? `${monthName(cursor.getMonth(), true)} ${cursor.getFullYear()}`
      : `Week of ${monthName(startOfWeek(cursor, settings.weekStartsOnMonday).getMonth())} ${startOfWeek(cursor, settings.weekStartsOnMonday).getDate()}`;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-1">
          <button onClick={() => step(-1)} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
            <ChevronLeft size={18} />
          </button>
          <button onClick={() => setCursor(today())} className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-sm">
            Today
          </button>
          <button onClick={() => step(1)} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
            <ChevronRight size={18} />
          </button>
          <h2 className="ml-2 font-semibold text-slate-700 dark:text-slate-200">{title}</h2>
        </div>
        <div className="flex gap-2">
          {(['month', 'week'] as const).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-3 py-1.5 rounded-lg border text-sm capitalize ${
                view === v ? 'bg-sky-500 text-white border-sky-500' : 'border-slate-200 dark:border-slate-700'
              }`}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      {view === 'month' ? (
        <MonthGrid cursor={cursor} byDay={byDay} mondayStart={settings.weekStartsOnMonday} onOpen={onOpen} />
      ) : (
        <WeekGrid cursor={cursor} byDay={byDay} mondayStart={settings.weekStartsOnMonday} onOpen={onOpen} />
      )}
    </div>
  );
}

function weekdayHeader(mondayStart: boolean): string[] {
  const base = [0, 1, 2, 3, 4, 5, 6].map((i) => weekdayShort(i));
  return mondayStart ? base : [base[6], ...base.slice(0, 6)];
}

function MonthGrid({
  cursor,
  byDay,
  mondayStart,
  onOpen,
}: {
  cursor: Date;
  byDay: Record<string, ElementDTO[]>;
  mondayStart: boolean;
  onOpen: (id: string) => void;
}) {
  const first = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
  const gridStart = startOfWeek(first, mondayStart);
  const days = Array.from({ length: 42 }, (_, i) => addDays(gridStart, i));
  const now = today();

  return (
    <div className="card p-2">
      <div className="grid grid-cols-7 gap-1 mb-1">
        {weekdayHeader(mondayStart).map((d) => (
          <div key={d} className="text-center text-xs font-medium text-slate-400 py-1">
            {d}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-1">
        {days.map((d) => {
          const items = byDay[isoDate(d)] ?? [];
          const inMonth = d.getMonth() === cursor.getMonth();
          return (
            <div
              key={isoDate(d)}
              className={`min-h-[92px] rounded-lg border p-1 ${
                inMonth ? 'border-slate-200/60 dark:border-slate-700' : 'border-transparent opacity-40'
              } ${sameDay(d, now) ? 'ring-2 ring-sky-400/60' : ''}`}
            >
              <div className="text-xs text-slate-400 mb-1">{d.getDate()}</div>
              <div className="space-y-1">
                {items.slice(0, 3).map((e) => (
                  <ElementView key={e.id} element={e} mode="line" onClick={onOpen} />
                ))}
                {items.length > 3 && (
                  <div className="text-[10px] text-slate-400">+{items.length - 3} more</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function WeekGrid({
  cursor,
  byDay,
  mondayStart,
  onOpen,
}: {
  cursor: Date;
  byDay: Record<string, ElementDTO[]>;
  mondayStart: boolean;
  onOpen: (id: string) => void;
}) {
  const start = startOfWeek(cursor, mondayStart);
  const days = Array.from({ length: 7 }, (_, i) => addDays(start, i));
  const now = today();
  return (
    <div className="grid grid-cols-1 md:grid-cols-7 gap-2">
      {days.map((d) => {
        const items = byDay[isoDate(d)] ?? [];
        return (
          <div key={isoDate(d)} className={`card p-2 min-h-[180px] ${sameDay(d, now) ? 'ring-2 ring-sky-400/60' : ''}`}>
            <div className="text-xs font-medium text-slate-500 mb-2">
              {weekdayShort((d.getDay() + 6) % 7)} {d.getDate()}
            </div>
            <div className="space-y-1">
              {items.map((e) => (
                <ElementView key={e.id} element={e} mode="line" onClick={onOpen} />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
