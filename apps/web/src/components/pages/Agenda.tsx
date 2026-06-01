import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, Clock, MapPin, AlertCircle, AlertTriangle } from "lucide-react";
import {
  format,
  startOfWeek,
  addDays,
  addWeeks,
  subWeeks,
  isSameDay,
  isToday,
} from "date-fns";
import { fetchApi } from "@/api/client";
import type { WeeklyView, DailyView, EventItem, TaskItem, Schedule } from "@/api/client";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getEventTime(schedules: Schedule[]): string | null {
  for (const s of schedules) {
    if (s.type === "single_day" && s.start_time) return s.start_time.slice(0, 5);
    if (s.type === "weekly" && s.appointments.length > 0) return s.appointments[0].start_time.slice(0, 5);
    if (s.type === "monthly") return s.start_time.slice(0, 5);
  }
  return null;
}

function getColor(layout: EventItem["effective_layout"]): string | null {
  return layout?.backgrounds?.[0]?.color ?? null;
}

const STATUS_COLORS: Record<string, string> = {
  todo: "text-amber-600 bg-amber-50 border-amber-200",
  in_progress: "text-blue-600 bg-blue-50 border-blue-200",
  done: "text-green-600 bg-green-50 border-green-200",
  cancelled: "text-muted-foreground bg-muted border-border line-through",
  blocked: "text-red-600 bg-red-50 border-red-200",
};

// ---------------------------------------------------------------------------
// Day cell content
// ---------------------------------------------------------------------------

function EventCard({ event, isConflicting }: { event: EventItem; isConflicting: boolean }) {
  const time = getEventTime(event.schedules);
  const color = getColor(event.effective_layout);

  return (
    <div
      className="p-2 rounded-lg border text-xs mb-1.5 relative"
      style={
        color
          ? { backgroundColor: color + "18", borderColor: color + "50" }
          : undefined
      }
    >
      {isConflicting && (
        <AlertTriangle className="absolute top-1.5 right-1.5 w-3 h-3 text-amber-500" />
      )}
      {time && (
        <div className="flex items-center gap-1 text-muted-foreground mb-0.5">
          <Clock className="w-3 h-3" />
          <span>{time}</span>
        </div>
      )}
      <p className="font-medium text-foreground leading-tight">{event.name}</p>
      {event.location && (
        <div className="flex items-center gap-1 text-muted-foreground mt-0.5">
          <MapPin className="w-3 h-3" />
          <span className="truncate">{event.location}</span>
        </div>
      )}
    </div>
  );
}

function TaskCard({ task }: { task: TaskItem }) {
  const statusClass = STATUS_COLORS[task.status] ?? STATUS_COLORS.todo;
  return (
    <div className={`p-2 rounded-lg border text-xs mb-1.5 ${statusClass}`}>
      <div className="flex items-start justify-between gap-1">
        <p className="font-medium leading-tight flex-1">{task.name}</p>
        <span className="capitalize shrink-0 opacity-80">{task.status.replace("_", " ")}</span>
      </div>
      {task.effective_deadline && (
        <p className="mt-0.5 opacity-70">Due {task.effective_deadline}</p>
      )}
    </div>
  );
}

function DayColumn({
  date,
  day,
  conflictIds,
  border,
}: {
  date: Date;
  day: DailyView | undefined;
  conflictIds: Set<string>;
  border?: "bottom" | "right" | "both" | "none";
}) {
  const today = isToday(date);
  const borderClass = {
    bottom: "border-b border-border",
    right: "border-r border-border",
    both: "border-b border-r border-border",
    none: "",
    undefined: "",
  }[border ?? "none"];

  return (
    <div className={`flex flex-col h-full ${borderClass}`}>
      {/* Header */}
      <div
        className={`px-3 py-2 border-b border-border flex items-center gap-2 ${
          today ? "bg-sidebar-primary/15" : "bg-muted/60"
        }`}
      >
        <div>
          <p className={`text-xs font-medium uppercase tracking-wide ${today ? "text-sidebar-primary" : "text-muted-foreground"}`}>
            {format(date, "EEE")}
          </p>
          <p className={`text-xl font-bold leading-none ${today ? "text-sidebar-primary" : "text-foreground"}`}>
            {format(date, "d")}
          </p>
        </div>
        {today && (
          <span className="ml-auto text-[10px] font-semibold px-1.5 py-0.5 rounded bg-sidebar-primary text-sidebar-primary-foreground">
            Today
          </span>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 p-2 overflow-y-auto">
        {(!day || (day.events.length === 0 && day.tasks.length === 0)) ? (
          <p className="text-xs text-muted-foreground/50 italic mt-1">—</p>
        ) : (
          <>
            {day.events.map((ev) => (
              <EventCard key={ev.id} event={ev} isConflicting={conflictIds.has(ev.id)} />
            ))}
            {day.tasks.map((t) => (
              <TaskCard key={t.id} task={t} />
            ))}
          </>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Loading skeleton that mirrors the notebook shape
// ---------------------------------------------------------------------------

function NotebookSkeleton() {
  return (
    <div className="flex gap-4 h-full">
      <div className="flex-1 bg-card rounded-l-2xl border border-border overflow-hidden">
        {[0, 1, 2].map((i) => (
          <div key={i} className={`h-1/3 p-3 ${i < 2 ? "border-b border-border/40" : ""}`}>
            <Skeleton className="h-4 w-12 mb-2" />
            <Skeleton className="h-8 w-8 mb-3 rounded" />
            <Skeleton className="h-10 w-full rounded-lg mb-2" />
            <Skeleton className="h-8 w-3/4 rounded-lg" />
          </div>
        ))}
      </div>
      <div className="w-5 bg-muted/50 rounded-sm" />
      <div className="flex-1 bg-card rounded-r-2xl border border-border overflow-hidden">
        {[0, 1].map((i) => (
          <div key={i} className="h-1/3 p-3 border-b border-border/40">
            <Skeleton className="h-4 w-12 mb-2" />
            <Skeleton className="h-8 w-8 mb-3 rounded" />
            <Skeleton className="h-10 w-full rounded-lg mb-2" />
          </div>
        ))}
        <div className="h-1/3 grid grid-cols-2 divide-x divide-border/40">
          {[0, 1].map((i) => (
            <div key={i} className="p-3">
              <Skeleton className="h-4 w-10 mb-2" />
              <Skeleton className="h-6 w-6 rounded mb-2" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Agenda page
// ---------------------------------------------------------------------------

export function Agenda() {
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const [weekData, setWeekData] = useState<WeeklyView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const weekStart = startOfWeek(currentWeek, { weekStartsOn: 1 });
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  useEffect(() => {
    setLoading(true);
    setError(null);
    const dateStr = format(weekStart, "yyyy-MM-dd");
    fetchApi<WeeklyView>(`/schedule/weekly?week_start=${dateStr}`)
      .then(setWeekData)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Unknown error"))
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weekStart.getTime()]);

  const dayMap = new Map(weekData?.days.map((d) => [d.date, d]) ?? []);

  // Build set of conflicting event IDs for the whole week
  const conflictIds = new Set<string>(
    weekData?.days.flatMap((d) =>
      d.conflicts.flatMap((c) => [c.blocker_id, c.blocked_id])
    ) ?? []
  );

  const hasConflicts = conflictIds.size > 0;

  if (error) {
    return (
      <div className="p-8 flex items-center gap-3 text-destructive">
        <AlertCircle className="w-5 h-5" />
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-6 bg-gradient-to-br from-background via-muted/20 to-background">
      {/* Header */}
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground mb-1">Agenda</h1>
          <p className="text-muted-foreground text-sm">Weekly planner</p>
        </div>

        {/* Week navigation */}
        <div className="flex items-center gap-2 bg-card border border-border rounded-xl px-4 py-2 shadow-sm">
          <button
            onClick={() => setCurrentWeek(subWeeks(currentWeek, 1))}
            className="p-1 hover:bg-muted rounded-lg transition-colors"
            title="Previous week"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <span className="text-sm font-medium min-w-[180px] text-center">
            {format(weekStart, "MMM d")} – {format(addDays(weekStart, 6), "MMM d, yyyy")}
          </span>

          <button
            onClick={() => setCurrentWeek(new Date())}
            className="text-xs px-2 py-1 bg-muted hover:bg-muted/80 rounded-md transition-colors font-medium"
          >
            Today
          </button>

          <button
            onClick={() => setCurrentWeek(addWeeks(currentWeek, 1))}
            className="p-1 hover:bg-muted rounded-lg transition-colors"
            title="Next week"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {hasConflicts && (
        <div className="mb-4 flex items-center gap-2 text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-sm">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>This week has scheduling conflicts — conflicting events are marked with a warning icon.</span>
        </div>
      )}

      {/* Notebook */}
      <div className="flex-1 min-h-0">
        {loading ? (
          <NotebookSkeleton />
        ) : (
          <div className="flex gap-4 h-full" style={{ perspective: "1800px" }}>
            {/* Left page — Mon, Tue, Wed */}
            <div
              className="flex-1 bg-card rounded-l-2xl border border-border overflow-hidden shadow-xl"
              style={{
                transform: "rotateY(1.5deg)",
                transformStyle: "preserve-3d",
                boxShadow: "0 16px 48px rgba(0,0,0,0.12), inset -8px 0 16px rgba(0,0,0,0.03)",
              }}
            >
              <div className="border-l-4 border-sidebar-primary/70 h-full grid grid-rows-3">
                {weekDays.slice(0, 3).map((date, i) => (
                  <DayColumn
                    key={i}
                    date={date}
                    day={dayMap.get(format(date, "yyyy-MM-dd"))}
                    conflictIds={conflictIds}
                    border={i < 2 ? "bottom" : "none"}
                  />
                ))}
              </div>
            </div>

            {/* Spine */}
            <div className="w-5 bg-gradient-to-b from-border via-muted-foreground/30 to-border rounded-sm shadow-inner relative flex-shrink-0">
              <div className="absolute inset-0 flex flex-col justify-around py-3">
                {Array.from({ length: 10 }).map((_, i) => (
                  <div key={i} className="h-0.5 bg-muted-foreground/20 mx-1 rounded-full" />
                ))}
              </div>
            </div>

            {/* Right page — Thu, Fri, Sat+Sun */}
            <div
              className="flex-1 bg-card rounded-r-2xl border border-border overflow-hidden shadow-xl"
              style={{
                transform: "rotateY(-1.5deg)",
                transformStyle: "preserve-3d",
                boxShadow: "0 16px 48px rgba(0,0,0,0.12), inset 8px 0 16px rgba(0,0,0,0.03)",
              }}
            >
              <div className="border-r-4 border-sidebar-primary/70 h-full grid grid-rows-3">
                {/* Thu */}
                <DayColumn
                  date={weekDays[3]}
                  day={dayMap.get(format(weekDays[3], "yyyy-MM-dd"))}
                  conflictIds={conflictIds}
                  border="bottom"
                />
                {/* Fri */}
                <DayColumn
                  date={weekDays[4]}
                  day={dayMap.get(format(weekDays[4], "yyyy-MM-dd"))}
                  conflictIds={conflictIds}
                  border="bottom"
                />
                {/* Sat + Sun side by side */}
                <div className="grid grid-cols-2 h-full divide-x divide-border">
                  <DayColumn
                    date={weekDays[5]}
                    day={dayMap.get(format(weekDays[5], "yyyy-MM-dd"))}
                    conflictIds={conflictIds}
                    border="right"
                  />
                  <DayColumn
                    date={weekDays[6]}
                    day={dayMap.get(format(weekDays[6], "yyyy-MM-dd"))}
                    conflictIds={conflictIds}
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
