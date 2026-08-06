import { useMemo } from 'react';
import { useData } from '../store';
import { useSettings } from '../settings';
import { ElementDTO } from '../types';
import { attrString, byType, displayName, isCancelled, whenOf } from '../lib/elements';
import { backgroundStyle, textOn } from '../lib/layout';
import { durationToMinutes, hasTime } from '../lib/format';

// The Timeboard organizes a *generic* week: the recurring events your schedules
// produce, collapsed onto one Mon–Sun timetable (like a class schedule).
// Real dated occurrences live in the Calendar; a single axis lives in Timeline.

const DAY_START = 7 * 60; // 07:00
const DAY_END = 22 * 60; // 22:00
const RANGE = DAY_END - DAY_START;
const PX_PER_MIN = 0.9; // ~54px per hour
const HEIGHT = RANGE * PX_PER_MIN;

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

interface Block {
  key: string;
  scheduleId: string;
  label: string;
  colIndex: number; // 0..6 in display order
  startMin: number;
  durMin: number;
  layout: ElementDTO['layout'];
}

function durationMinutes(s: string | undefined): number {
  return durationToMinutes(s) || 60;
}

export function Timeboard({ onOpen }: { onOpen: (id: string) => void }) {
  const { elements, byId } = useData();
  const { settings } = useSettings();
  const mondayStart = settings.weekStartsOnMonday;

  const dayOrder = useMemo(
    () => (mondayStart ? [0, 1, 2, 3, 4, 5, 6] : [6, 0, 1, 2, 3, 4, 5]),
    [mondayStart],
  );

  const { timed, allDay } = useMemo(() => {
    const scheduleEvents = byType(elements, 'event').filter(
      (e) => !isCancelled(e) && e.mainParent && byId[e.mainParent]?.type === 'schedule',
    );
    const timedMap = new Map<string, Block>();
    const allDayMap = new Map<string, { scheduleId: string; colIndex: number; label: string; layout: ElementDTO['layout'] }>();

    for (const e of scheduleEvents) {
      const d = whenOf(e);
      if (!d || !e.mainParent) continue;
      const monIdx = (d.getDay() + 6) % 7; // 0 = Mon
      const colIndex = mondayStart ? monIdx : (monIdx + 1) % 7;
      const label = displayName(byId[e.mainParent]);
      if (!hasTime(attrString(e, 'start'))) {
        const key = `${e.mainParent}|${colIndex}`;
        if (!allDayMap.has(key)) allDayMap.set(key, { scheduleId: e.mainParent, colIndex, label, layout: e.layout });
        continue;
      }
      const startMin = d.getHours() * 60 + d.getMinutes();
      const key = `${e.mainParent}|${monIdx}|${startMin}`;
      if (!timedMap.has(key)) {
        timedMap.set(key, {
          key,
          scheduleId: e.mainParent,
          label,
          colIndex,
          startMin,
          durMin: durationMinutes(attrString(e, 'duration')),
          layout: e.layout,
        });
      }
    }
    return { timed: [...timedMap.values()], allDay: [...allDayMap.values()] };
  }, [elements, byId, mondayStart]);

  const hours = Array.from({ length: (DAY_END - DAY_START) / 60 + 1 }, (_, i) => 7 + i);

  if (byType(elements, 'schedule').length === 0) {
    return <div className="card p-8 text-center text-slate-400">No schedules to lay out.</div>;
  }

  return (
    <div className="card p-4 overflow-x-auto">
      <p className="text-sm text-slate-500 mb-3">
        A generic week built from your schedules — recurring events collapsed onto one timetable.
      </p>
      <div className="min-w-[720px]">
        {/* weekday headers */}
        <div className="grid" style={{ gridTemplateColumns: `48px repeat(7, minmax(0,1fr))` }}>
          <div />
          {dayOrder.map((d) => (
            <div key={d} className="text-center text-sm font-semibold text-slate-600 dark:text-slate-300 pb-2">
              {WEEKDAY_LABELS[d]}
            </div>
          ))}
        </div>

        {/* all-day row */}
        {allDay.length > 0 && (
          <div className="grid mb-1" style={{ gridTemplateColumns: `48px repeat(7, minmax(0,1fr))` }}>
            <div className="text-[10px] text-slate-400 pr-1 text-right">all day</div>
            {dayOrder.map((_, col) => (
              <div key={col} className="px-1 space-y-1">
                {allDay
                  .filter((a) => a.colIndex === col)
                  .map((a) => (
                    <button
                      key={a.scheduleId}
                      onClick={() => onOpen(a.scheduleId)}
                      className="w-full text-left text-xs rounded px-1.5 py-0.5 truncate border border-slate-200/60 dark:border-slate-700"
                      style={{ ...backgroundStyle(a.layout), color: textOn(a.layout) }}
                    >
                      {a.label}
                    </button>
                  ))}
              </div>
            ))}
          </div>
        )}

        {/* timed grid */}
        <div className="grid" style={{ gridTemplateColumns: `48px repeat(7, minmax(0,1fr))` }}>
          {/* hour gutter */}
          <div className="relative" style={{ height: HEIGHT }}>
            {hours.map((h) => (
              <div
                key={h}
                className="absolute right-1 -translate-y-1/2 text-[10px] text-slate-400"
                style={{ top: (h * 60 - DAY_START) * PX_PER_MIN }}
              >
                {String(h).padStart(2, '0')}:00
              </div>
            ))}
          </div>
          {/* day columns */}
          {dayOrder.map((_, col) => (
            <div
              key={col}
              className="relative border-l border-slate-200/50 dark:border-slate-700"
              style={{ height: HEIGHT }}
            >
              {hours.map((h) => (
                <div
                  key={h}
                  className="absolute left-0 right-0 border-t border-slate-100 dark:border-slate-800"
                  style={{ top: (h * 60 - DAY_START) * PX_PER_MIN }}
                />
              ))}
              {timed
                .filter((b) => b.colIndex === col)
                .map((b) => {
                  const top = Math.max(0, (b.startMin - DAY_START) * PX_PER_MIN);
                  const height = Math.max(18, b.durMin * PX_PER_MIN);
                  return (
                    <button
                      key={b.key}
                      onClick={() => onOpen(b.scheduleId)}
                      className="absolute left-0.5 right-0.5 rounded-md px-1.5 py-0.5 text-xs text-left overflow-hidden border border-slate-300/50 hover:z-10 hover:ring-2 hover:ring-sky-400/50"
                      style={{ top, height, ...backgroundStyle(b.layout), color: textOn(b.layout) }}
                      title={b.label}
                    >
                      <span className="font-medium">{b.label}</span>
                      <span className="block opacity-80">
                        {String(Math.floor(b.startMin / 60)).padStart(2, '0')}:
                        {String(b.startMin % 60).padStart(2, '0')}
                      </span>
                    </button>
                  );
                })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
