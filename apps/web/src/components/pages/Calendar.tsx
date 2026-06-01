import { useState, useEffect, useMemo } from "react";
import { ChevronLeft, ChevronRight, AlertCircle, Clock, MapPin } from "lucide-react";
import {
  format,
  startOfWeek,
  addDays,
  addMonths,
  addYears,
  getDay,
  isToday,
  startOfMonth,
  endOfMonth,
  startOfYear,
  endOfYear,
} from "date-fns";
import { fetchApi } from "@/api/client";
import type { DailyView, EventItem, TaskItem, Schedule } from "@/api/client";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/components/ui/utils";

// ---------------------------------------------------------------------------
// Types & constants
// ---------------------------------------------------------------------------

type ViewMode = "daily" | "weekly" | "monthly" | "yearly";

const DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];
const TASK_DOT: Record<string, string> = {
  todo: "#f59e0b",
  in_progress: "#3b82f6",
  done: "#10b981",
  blocked: "#ef4444",
  cancelled: "#9ca3af",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function eventColor(ev: EventItem): string {
  return ev.effective_layout?.backgrounds?.[0]?.color ?? "#6366f1";
}

function getEventTime(schedules: Schedule[]): string | null {
  for (const s of schedules) {
    if (s.type === "single_day" && s.start_time) return s.start_time.slice(0, 5);
    if (s.type === "weekly" && s.appointments.length > 0) return s.appointments[0].start_time.slice(0, 5);
    if (s.type === "monthly") return s.start_time.slice(0, 5);
  }
  return null;
}

function getDateRange(date: Date, mode: ViewMode): [Date, Date] {
  switch (mode) {
    case "daily":   return [date, date];
    case "weekly": { const s = startOfWeek(date, { weekStartsOn: 1 }); return [s, addDays(s, 6)]; }
    case "monthly": return [startOfMonth(date), endOfMonth(date)];
    case "yearly":  return [startOfYear(date), endOfYear(date)];
  }
}

function navLabel(date: Date, mode: ViewMode): string {
  switch (mode) {
    case "daily":   return format(date, "EEEE, MMMM d, yyyy");
    case "weekly": { const s = startOfWeek(date, { weekStartsOn: 1 }); return `${format(s, "MMM d")} – ${format(addDays(s, 6), "MMM d, yyyy")}`; }
    case "monthly": return format(date, "MMMM yyyy");
    case "yearly":  return format(date, "yyyy");
  }
}

function parseDateStr(str: string): Date {
  const [y, m, d] = str.split("-").map(Number);
  return new Date(y, m - 1, d);
}

// ---------------------------------------------------------------------------
// Dot indicators
// ---------------------------------------------------------------------------

function DayDots({ day, mini }: { day: DailyView; mini?: boolean }) {
  if (mini) {
    const hasAny = day.events.length > 0 || day.tasks.some(t => t.status !== "cancelled");
    if (!hasAny) return null;
    const color = day.events[0] ? eventColor(day.events[0]) : TASK_DOT[day.tasks[0]?.status] ?? "#6366f1";
    return <div className="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full" style={{ backgroundColor: color }} />;
  }

  const dots = [
    ...day.events.map(e => eventColor(e)),
    ...day.tasks.filter(t => t.status !== "cancelled").map(t => TASK_DOT[t.status] ?? "#94a3b8"),
  ].slice(0, 5);

  if (dots.length === 0) return null;
  return (
    <div className="flex flex-wrap justify-center gap-0.5 mt-0.5">
      {dots.map((c, i) => <div key={i} className="rounded-full" style={{ width: 5, height: 5, backgroundColor: c }} />)}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Detail panel (side panel for monthly view)
// ---------------------------------------------------------------------------

function EventRow({ ev }: { ev: EventItem }) {
  const time = getEventTime(ev.schedules);
  const color = eventColor(ev);
  return (
    <div className="flex items-start gap-2.5 py-2 border-b border-border/50 last:border-0">
      <div className="w-2.5 h-2.5 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: color }} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium leading-tight">{ev.name}</p>
        <div className="flex flex-wrap gap-x-2 mt-0.5">
          {time && <span className="flex items-center gap-0.5 text-xs text-muted-foreground"><Clock className="w-3 h-3" />{time}</span>}
          {ev.location && <span className="flex items-center gap-0.5 text-xs text-muted-foreground truncate"><MapPin className="w-3 h-3" />{ev.location}</span>}
        </div>
      </div>
    </div>
  );
}

function TaskRow({ task }: { task: TaskItem }) {
  return (
    <div className="flex items-start gap-2.5 py-2 border-b border-border/50 last:border-0">
      <div className="w-2 h-2 rounded-sm mt-1.5 flex-shrink-0" style={{ backgroundColor: TASK_DOT[task.status] ?? "#94a3b8" }} />
      <div className="flex-1 min-w-0">
        <p className={cn("text-sm font-medium leading-tight", task.status === "cancelled" && "line-through text-muted-foreground")}>
          {task.name}
        </p>
        <div className="flex gap-2 mt-0.5">
          <span className="text-xs text-muted-foreground capitalize">{task.status.replace("_", " ")}</span>
          {task.effective_deadline && <span className="text-xs text-muted-foreground">· {task.effective_deadline}</span>}
        </div>
      </div>
    </div>
  );
}

function DayDetailPanel({ dateStr, day }: { dateStr: string | null; day: DailyView | null }) {
  if (!dateStr) {
    return (
      <div className="bg-card rounded-xl border border-border h-full flex items-center justify-center p-6">
        <p className="text-muted-foreground text-sm text-center">Hover or click a day<br />to see details</p>
      </div>
    );
  }
  const date = parseDateStr(dateStr);
  const events = day?.events ?? [];
  const tasks = day?.tasks ?? [];

  return (
    <div className="bg-card rounded-xl border border-border h-full flex flex-col overflow-hidden">
      <div className="px-4 py-3 border-b border-border bg-muted/40 flex-shrink-0">
        <p className="font-semibold text-sm">{format(date, "EEEE")}</p>
        <p className="text-xs text-muted-foreground">{format(date, "MMMM d, yyyy")}</p>
      </div>
      <div className="flex-1 overflow-y-auto px-4 py-3">
        {events.length === 0 && tasks.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center mt-6">No events or tasks</p>
        ) : (
          <>
            {events.length > 0 && (
              <div className="mb-4">
                <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Events ({events.length})</p>
                {events.map(ev => <EventRow key={ev.id} ev={ev} />)}
              </div>
            )}
            {tasks.length > 0 && (
              <div>
                <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Tasks ({tasks.length})</p>
                {tasks.map(t => <TaskRow key={t.id} task={t} />)}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Month grid (full and mini)
// ---------------------------------------------------------------------------

function MonthGrid({
  year, month, dayMap, selectedDate, hoveredDate, onSelect, onHover, mini, onClickMini,
}: {
  year: number; month: number;
  dayMap: Map<string, DailyView>;
  selectedDate: string | null; hoveredDate: string | null;
  onSelect: (d: string) => void; onHover: (d: string | null) => void;
  mini?: boolean; onClickMini?: () => void;
}) {
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const startOffset = (getDay(new Date(year, month, 1)) + 6) % 7; // Mon-based
  const cells: (number | null)[] = [...Array(startOffset).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)];
  while (cells.length % 7 !== 0) cells.push(null);

  return (
    <div className={cn(mini && onClickMini && "cursor-pointer")} onClick={mini && onClickMini ? onClickMini : undefined}>
      {mini && <p className="text-[11px] font-semibold text-center mb-1 text-muted-foreground">{MONTH_NAMES[month].slice(0, 3)}</p>}
      {/* DOW header */}
      <div className="grid grid-cols-7">
        {DOW.map(d => (
          <div key={d} className={cn("text-center font-medium text-muted-foreground", mini ? "text-[9px] py-0.5" : "text-xs py-1.5")}>
            {mini ? d[0] : d}
          </div>
        ))}
      </div>
      {/* Day cells */}
      <div className={cn("grid grid-cols-7", mini ? "gap-px" : "gap-0.5")}>
        {cells.map((day, idx) => {
          if (!day) return <div key={idx} />;
          const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
          const dayData = dayMap.get(dateStr);
          const today = isToday(new Date(year, month, day));
          const isSelected = selectedDate === dateStr;
          const isHovered = hoveredDate === dateStr;

          if (mini) {
            return (
              <div key={idx} className="relative aspect-square flex items-center justify-center">
                <span className={cn("text-[9px] leading-none", today ? "text-sidebar-primary font-bold" : "text-foreground/70")}>{day}</span>
                {dayData && <DayDots day={dayData} mini />}
              </div>
            );
          }

          return (
            <div
              key={idx}
              className={cn(
                "relative aspect-square p-1 rounded-lg cursor-pointer transition-all duration-150 hover:bg-muted/60",
                today && "ring-2 ring-sidebar-primary",
                (isSelected || isHovered) && "bg-sidebar-primary/10",
              )}
              onMouseEnter={() => onHover(dateStr)}
              onMouseLeave={() => onHover(null)}
              onClick={e => { e.stopPropagation(); onSelect(dateStr); }}
            >
              <span className={cn("block text-center text-xs font-medium", today ? "text-sidebar-primary font-bold" : "text-foreground")}>
                {day}
              </span>
              {dayData && <DayDots day={dayData} />}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Week grid (7 columns)
// ---------------------------------------------------------------------------

function WeekGrid({
  weekStart, dayMap, selectedDate, hoveredDate, onSelect, onHover,
}: {
  weekStart: Date; dayMap: Map<string, DailyView>;
  selectedDate: string | null; hoveredDate: string | null;
  onSelect: (d: string) => void; onHover: (d: string | null) => void;
}) {
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  return (
    <div className="flex-1 grid grid-cols-7 gap-2 min-h-0">
      {days.map(date => {
        const dateStr = format(date, "yyyy-MM-dd");
        const day = dayMap.get(dateStr);
        const today = isToday(date);
        const active = selectedDate === dateStr || hoveredDate === dateStr;
        const events = day?.events ?? [];
        const tasks = day?.tasks ?? [];

        return (
          <div
            key={dateStr}
            className={cn(
              "flex flex-col bg-card border border-border rounded-xl overflow-hidden cursor-pointer transition-all duration-150",
              today && "border-sidebar-primary",
              active && "ring-2 ring-sidebar-primary/50 shadow-md",
            )}
            onMouseEnter={() => onHover(dateStr)}
            onMouseLeave={() => onHover(null)}
            onClick={() => onSelect(dateStr)}
          >
            <div className={cn("px-2 py-2 text-center border-b border-border flex-shrink-0", today ? "bg-sidebar-primary/10" : "bg-muted/40")}>
              <p className={cn("text-[11px] font-medium uppercase tracking-wide", today ? "text-sidebar-primary" : "text-muted-foreground")}>{format(date, "EEE")}</p>
              <p className={cn("text-lg font-bold leading-tight", today ? "text-sidebar-primary" : "text-foreground")}>{format(date, "d")}</p>
            </div>
            <div className="flex-1 p-1.5 overflow-y-auto space-y-1" style={{ scrollbarWidth: "none" }}>
              {events.map(ev => (
                <div key={ev.id} className="rounded px-1.5 py-1 text-xs truncate font-medium"
                  style={{ backgroundColor: eventColor(ev) + "22", borderLeft: `2px solid ${eventColor(ev)}`, color: "inherit" }}>
                  {ev.name}
                </div>
              ))}
              {tasks.map(t => (
                <div key={t.id} className="flex items-center gap-1 rounded px-1.5 py-1 text-xs bg-muted">
                  <div className="w-1.5 h-1.5 rounded-sm flex-shrink-0" style={{ backgroundColor: TASK_DOT[t.status] }} />
                  <span className={cn("truncate", t.status === "cancelled" && "line-through text-muted-foreground")}>{t.name}</span>
                </div>
              ))}
              {events.length === 0 && tasks.length === 0 && (
                <p className="text-[10px] text-muted-foreground/30 text-center mt-3 italic">—</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Daily detail panel (full-width, for daily view)
// ---------------------------------------------------------------------------

function DailyFullPanel({ dateStr, day }: { dateStr: string; day: DailyView | null }) {
  const date = parseDateStr(dateStr);
  const events = day?.events ?? [];
  const tasks = day?.tasks ?? [];

  return (
    <div className="flex-1 bg-card rounded-xl border border-border overflow-hidden flex flex-col min-h-0">
      <div className="px-6 py-4 border-b border-border bg-muted/40 flex-shrink-0">
        <p className="text-xl font-semibold">{format(date, "EEEE")}</p>
        <p className="text-muted-foreground text-sm">{format(date, "MMMM d, yyyy")}</p>
      </div>
      <div className="flex-1 overflow-y-auto px-6 py-5">
        {events.length === 0 && tasks.length === 0 ? (
          <p className="text-muted-foreground text-sm">No events or tasks scheduled for this day.</p>
        ) : (
          <div className="grid grid-cols-2 gap-8">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Events ({events.length})</p>
              {events.length === 0 ? <p className="text-sm text-muted-foreground">None</p> : events.map(ev => <EventRow key={ev.id} ev={ev} />)}
            </div>
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Tasks ({tasks.length})</p>
              {tasks.length === 0 ? <p className="text-sm text-muted-foreground">None</p> : tasks.map(t => <TaskRow key={t.id} task={t} />)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Calendar page
// ---------------------------------------------------------------------------

export function Calendar() {
  const [viewMode, setViewMode] = useState<ViewMode>("monthly");
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [hoveredDate, setHoveredDate] = useState<string | null>(null);
  const [dayMap, setDayMap] = useState<Map<string, DailyView>>(new Map());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Stable range key — re-fetch only when the visible range actually changes
  const [rangeStart, rangeEnd] = useMemo(() => {
    const [s, e] = getDateRange(currentDate, viewMode);
    return [format(s, "yyyy-MM-dd"), format(e, "yyyy-MM-dd")];
  }, [viewMode, currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate()]);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchApi<DailyView[]>(`/schedule/range?start=${rangeStart}&end=${rangeEnd}`)
      .then(days => setDayMap(new Map(days.map(d => [d.date, d]))))
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, [rangeStart, rangeEnd]);

  function navigate(dir: 1 | -1) {
    setCurrentDate(prev => {
      switch (viewMode) {
        case "daily":   return addDays(prev, dir);
        case "weekly":  return addDays(prev, dir * 7);
        case "monthly": return addMonths(prev, dir);
        case "yearly":  return addYears(prev, dir);
      }
    });
  }

  const weekStart = useMemo(() => startOfWeek(currentDate, { weekStartsOn: 1 }), [currentDate]);
  const activeDate = hoveredDate ?? selectedDate;
  const activeDayData = activeDate ? (dayMap.get(activeDate) ?? null) : null;

  if (error) {
    return (
      <div className="p-8 flex items-center gap-3 text-destructive">
        <AlertCircle className="w-5 h-5" /><span>{error}</span>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-6 bg-gradient-to-br from-background via-muted/20 to-background">
      {/* ── Header ── */}
      <div className="mb-5 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground mb-1">Calendar</h1>
            <p className="text-muted-foreground text-sm">Schedule overview</p>
          </div>
          {/* View mode tabs */}
          <div className="flex gap-1 bg-muted/60 p-1 rounded-lg">
            {(["daily", "weekly", "monthly", "yearly"] as ViewMode[]).map(mode => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={cn(
                  "px-3 py-1.5 rounded-md text-sm capitalize transition-all duration-200",
                  viewMode === mode ? "bg-sidebar-primary text-sidebar-primary-foreground shadow" : "hover:bg-muted text-muted-foreground"
                )}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>

        {/* Navigation bar */}
        <div className="flex items-center justify-between bg-card border border-border rounded-xl px-4 py-2.5 shadow-sm">
          <button onClick={() => navigate(-1)} className="p-1.5 hover:bg-muted rounded-lg transition-colors">
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-sm font-semibold">{navLabel(currentDate, viewMode)}</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => { setCurrentDate(new Date()); setSelectedDate(format(new Date(), "yyyy-MM-dd")); }}
              className="text-xs px-2 py-1 bg-muted hover:bg-muted/80 rounded-md transition-colors font-medium"
            >
              Today
            </button>
            <button onClick={() => navigate(1)} className="p-1.5 hover:bg-muted rounded-lg transition-colors">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* ── Main content ── */}
      {loading ? (
        <div className="flex-1 bg-card rounded-xl border border-border flex items-center justify-center">
          <div className="space-y-4 w-full max-w-sm px-8">
            <Skeleton className="h-6 w-40 mx-auto" />
            <div className="grid grid-cols-7 gap-1.5">
              {Array.from({ length: 35 }).map((_, i) => <Skeleton key={i} className="aspect-square rounded-lg opacity-40" />)}
            </div>
          </div>
        </div>
      ) : (
        <div className={cn("flex-1 min-h-0 flex gap-4", viewMode === "monthly" ? "flex-row" : "flex-col")}>

          {/* ── Monthly view ── */}
          {viewMode === "monthly" && (
            <>
              <div className="flex-1 bg-card border border-border rounded-xl p-5 overflow-auto">
                <MonthGrid
                  year={currentDate.getFullYear()} month={currentDate.getMonth()}
                  dayMap={dayMap} selectedDate={selectedDate} hoveredDate={hoveredDate}
                  onSelect={setSelectedDate} onHover={setHoveredDate}
                />
              </div>
              <div className="w-64 flex-shrink-0">
                <DayDetailPanel dateStr={activeDate} day={activeDayData} />
              </div>
            </>
          )}

          {/* ── Weekly view ── */}
          {viewMode === "weekly" && (
            <WeekGrid
              weekStart={weekStart} dayMap={dayMap}
              selectedDate={selectedDate} hoveredDate={hoveredDate}
              onSelect={setSelectedDate} onHover={setHoveredDate}
            />
          )}

          {/* ── Daily view ── */}
          {viewMode === "daily" && (
            <DailyFullPanel dateStr={format(currentDate, "yyyy-MM-dd")} day={dayMap.get(format(currentDate, "yyyy-MM-dd")) ?? null} />
          )}

          {/* ── Yearly view ── */}
          {viewMode === "yearly" && (
            <div className="flex-1 bg-card border border-border rounded-xl p-5 overflow-auto">
              <div className="grid grid-cols-4 gap-5">
                {Array.from({ length: 12 }, (_, i) => (
                  <div
                    key={i}
                    className="bg-muted/30 rounded-lg p-3 border border-border hover:bg-muted/50 transition-colors cursor-pointer"
                    onClick={() => { setCurrentDate(new Date(currentDate.getFullYear(), i, 1)); setViewMode("monthly"); }}
                  >
                    <MonthGrid
                      year={currentDate.getFullYear()} month={i}
                      dayMap={dayMap} selectedDate={null} hoveredDate={null}
                      onSelect={() => { setCurrentDate(new Date(currentDate.getFullYear(), i, 1)); setViewMode("monthly"); }}
                      onHover={() => {}}
                      mini
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
