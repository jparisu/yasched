import { useEffect, useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { fetchEventsRange, baseId } from '../api/client';
import { useEditor } from '../data/EditorContext';
import { useElement } from '../data/ElementContext';
import { DisplayItem } from '../components/ui';
import { Density, DisplayStyle, EventItem } from '../types';

const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const HOUR_PX = 52;

function toMinutes(hhmm: string | null | undefined): number | null {
  if (!hhmm) return null;
  const [h, m] = hhmm.split(':').map(Number);
  if (Number.isNaN(h)) return null;
  return h * 60 + (m || 0);
}

const isoOf = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

/** Monday (00:00 local) of the week containing `d`. */
function mondayOf(d: Date): Date {
  const x = new Date(d);
  const dow = x.getDay();
  x.setDate(x.getDate() - dow + (dow === 0 ? -6 : 1));
  x.setHours(0, 0, 0, 0);
  return x;
}

export function WeekTimetable() {
  const { openEdit } = useEditor();
  const { openElement } = useElement();
  const displayStyle = 'line' as DisplayStyle;
  const density = 'comfortable' as Density;
  const [weekStart, setWeekStart] = useState(() => mondayOf(new Date()));
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showWeekend, setShowWeekend] = useState(false);

  // The seven dates of the visible week (Mon..Sun).
  const weekDates = useMemo(
    () =>
      Array.from({ length: 7 }, (_, i) => {
        const d = new Date(weekStart);
        d.setDate(d.getDate() + i);
        return d;
      }),
    [weekStart]
  );

  // Fetch the concrete dated occurrences for exactly this week — so recurrence
  // bounds, sub-event overrides and cancellations are all reflected, and
  // navigating to another week shows that week's events.
  useEffect(() => {
    setLoading(true);
    fetchEventsRange(isoOf(weekDates[0]), isoOf(weekDates[6]))
      .then(setEvents)
      .finally(() => setLoading(false));
  }, [weekDates]);

  const dayIndexOf = (d: Date) => (d.getDay() + 6) % 7; // 0 = Mon
  const eventsOnDay = (dayIdx: number) =>
    events.filter((e) => dayIndexOf(new Date(e.date)) === dayIdx);

  const days = showWeekend ? [0, 1, 2, 3, 4, 5, 6] : [0, 1, 2, 3, 4];

  const timed = events.filter((e) => toMinutes(e.startTime) !== null);
  const starts = timed.map((e) => toMinutes(e.startTime) as number);
  const ends = timed.map((e) => toMinutes(e.endTime) ?? (toMinutes(e.startTime) as number) + 60);
  const startHour = starts.length ? Math.max(0, Math.floor(Math.min(...starts) / 60)) : 8;
  const endHour = ends.length ? Math.min(24, Math.ceil(Math.max(...ends) / 60)) : 18;
  const hours = Array.from({ length: Math.max(1, endHour - startHour) }, (_, i) => startHour + i);
  const gridHeight = hours.length * HOUR_PX;
  const gap = density === 'compact' ? 1 : 2;

  const allDayByDay = (day: number) =>
    eventsOnDay(day).filter((e) => toMinutes(e.startTime) === null);
  const timedByDay = (day: number) =>
    eventsOnDay(day).filter((e) => toMinutes(e.startTime) !== null);

  const shiftWeek = (delta: number) => {
    const d = new Date(weekStart);
    d.setDate(d.getDate() + delta * 7);
    setWeekStart(d);
  };
  const today = new Date();
  const isToday = (d: number) => weekDates[d].toDateString() === today.toDateString();
  const rangeLabel = `${weekDates[0].toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} – ${weekDates[6].toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;

  return (
    <div className="max-w-6xl mx-auto space-y-4">
      {/* week navigator */}
      <div className="flex items-center gap-2 flex-wrap">
        <button onClick={() => shiftWeek(-1)} className="p-2 rounded-lg bg-teal-100 dark:bg-teal-900/30 text-teal-600 hover:bg-teal-200 dark:hover:bg-teal-900/50 transition-colors">
          <ChevronLeft size={18} />
        </button>
        <button
          onClick={() => setWeekStart(mondayOf(new Date()))}
          className="px-4 py-2 text-sm font-semibold rounded-lg shadow-md bg-gradient-to-r from-sky-400 to-lavender-500 text-white hover:shadow-lg transition-shadow"
        >
          This week
        </button>
        <button onClick={() => shiftWeek(1)} className="p-2 rounded-lg bg-teal-100 dark:bg-teal-900/30 text-teal-600 hover:bg-teal-200 dark:hover:bg-teal-900/50 transition-colors">
          <ChevronRight size={18} />
        </button>
        <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 ml-2">{rangeLabel}</h2>
        <label className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300 ml-auto">
          <input type="checkbox" checked={showWeekend} onChange={(e) => setShowWeekend(e.target.checked)} />
          Weekends
        </label>
      </div>

      {loading ? (
        <div className="py-16 text-center text-slate-400">Loading…</div>
      ) : events.length === 0 ? (
        <div className="py-16 text-center text-slate-400">No events this week.</div>
      ) : (
        <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-x-auto">
          <div className="min-w-[640px]">
            {/* header */}
            <div className="grid" style={{ gridTemplateColumns: `56px repeat(${days.length}, 1fr)` }}>
              <div className="border-b border-slate-200 dark:border-slate-800" />
              {days.map((d) => {
                const date = weekDates[d];
                const todayCol = isToday(d);
                return (
                  <div
                    key={d}
                    className={`border-b border-l border-slate-200 dark:border-slate-800 py-2 text-center text-sm font-semibold flex items-center justify-center gap-1.5 ${
                      todayCol ? 'bg-sky-50 dark:bg-sky-900/20 text-slate-700 dark:text-slate-200' : 'text-slate-700 dark:text-slate-200'
                    }`}
                  >
                    {DAY_NAMES[d]}
                    <span
                      className={
                        todayCol
                          ? 'inline-flex items-center justify-center w-6 h-6 rounded-full bg-gradient-to-br from-sky-400 to-lavender-500 text-white text-xs font-bold'
                          : ''
                      }
                    >
                      {date.getDate()}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* all-day row */}
            {days.some((d) => allDayByDay(d).length > 0) && (
              <div className="grid" style={{ gridTemplateColumns: `56px repeat(${days.length}, 1fr)` }}>
                <div className="text-[10px] text-slate-400 flex items-center justify-center border-b border-slate-100 dark:border-slate-800">
                  all-day
                </div>
                {days.map((d) => (
                  <div key={d} className="border-l border-b border-slate-100 dark:border-slate-800 p-1 space-y-1">
                    {allDayByDay(d).map((e) => (
                      <DisplayItem
                        key={e.id}
                        title={e.title}
                        displayStyle={displayStyle}
                        itemStyle={e.style}
                        recurring={e.recurring}
                        onClick={() => openEdit('events', baseId(e.id))}
                        onDoubleClick={() => openElement('events', baseId(e.id))}
                      />
                    ))}
                  </div>
                ))}
              </div>
            )}

            {/* time grid */}
            <div className="grid" style={{ gridTemplateColumns: `56px repeat(${days.length}, 1fr)` }}>
              <div className="relative" style={{ height: gridHeight }}>
                {hours.map((h, i) => (
                  <div
                    key={h}
                    className="absolute right-1 text-[10px] text-slate-400 -translate-y-1/2"
                    style={{ top: i * HOUR_PX }}
                  >
                    {String(h).padStart(2, '0')}:00
                  </div>
                ))}
              </div>

              {days.map((d) => (
                <div
                  key={d}
                  className={`relative border-l border-slate-200 dark:border-slate-800 ${
                    isToday(d) ? 'bg-sky-50/60 dark:bg-sky-900/10' : ''
                  }`}
                  style={{ height: gridHeight }}
                >
                  {hours.map((_, i) => (
                    <div
                      key={i}
                      className="absolute w-full border-t border-slate-100 dark:border-slate-800/60"
                      style={{ top: i * HOUR_PX }}
                    />
                  ))}
                  {timedByDay(d).map((e) => {
                    const start = toMinutes(e.startTime) as number;
                    const end = toMinutes(e.endTime) ?? start + 60;
                    const top = ((start - startHour * 60) / 60) * HOUR_PX;
                    const height = Math.max(18, ((end - start) / 60) * HOUR_PX - gap);
                    return (
                      <div key={e.id} className="absolute left-1 right-1" style={{ top, height }}>
                        <DisplayItem
                          title={e.title}
                          displayStyle={displayStyle}
                          itemStyle={e.style}
                          startTime={e.startTime ?? undefined}
                          endTime={e.endTime ?? undefined}
                          recurring={e.recurring}
                          onClick={() => openEdit('events', baseId(e.id))}
                          onDoubleClick={() => openElement('events', baseId(e.id))}
                          className="h-full overflow-hidden"
                        />
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
