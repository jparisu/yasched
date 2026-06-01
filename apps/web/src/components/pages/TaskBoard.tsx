import { useState, useEffect, useMemo } from "react";
import { Search, AlertCircle } from "lucide-react";
import { fetchApi } from "@/api/client";
import type { TaskItem, Topic } from "@/api/client";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/components/ui/utils";

// ---------------------------------------------------------------------------
// Status config
// ---------------------------------------------------------------------------

const STATUSES = [
  { id: "todo",        label: "To Do",       pin: "bg-yellow-400", bg: "bg-yellow-50",  border: "border-yellow-300" },
  { id: "in_progress", label: "In Progress", pin: "bg-blue-500",   bg: "bg-blue-50",    border: "border-blue-300"   },
  { id: "done",        label: "Done",        pin: "bg-green-500",  bg: "bg-green-50",   border: "border-green-300"  },
  { id: "blocked",     label: "Blocked",     pin: "bg-red-500",    bg: "bg-red-50",     border: "border-red-300"    },
  { id: "cancelled",   label: "Cancelled",   pin: "bg-gray-400",   bg: "bg-gray-50",    border: "border-gray-300"   },
] as const;

// Deterministic stable rotation per task id
function cardRotation(id: string): number {
  const h = id.split("").reduce((a, c) => a + c.charCodeAt(0), 0);
  return ((h % 13) - 6) * 0.45; // -2.7° to +2.7°
}

// ---------------------------------------------------------------------------
// Task card (post-it)
// ---------------------------------------------------------------------------

function TaskCard({
  task,
  status,
  topicMap,
}: {
  task: TaskItem;
  status: (typeof STATUSES)[number];
  topicMap: Map<string, Topic>;
}) {
  const rot = cardRotation(task.id);
  const topicColor = task.effective_layout?.backgrounds?.[0]?.color ?? null;
  const topicName = task.topic_ids[0] ? topicMap.get(task.topic_ids[0])?.name : null;
  const isCancelled = task.status === "cancelled";

  return (
    <div className="relative mb-5 mx-3" style={{ transform: `rotate(${rot}deg)` }}>
      {/* Pin */}
      <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center">
        <div
          className={cn("w-5 h-5 rounded-full shadow-md relative border border-black/10", !topicColor && status.pin)}
          style={topicColor ? { backgroundColor: topicColor } : undefined}
        >
          <div className="absolute top-1 left-1 w-1.5 h-1.5 rounded-full bg-white/50" />
        </div>
        <div className="w-px h-2 bg-gray-400" />
      </div>

      {/* Post-it body */}
      <div
        className={cn("pt-4 pb-3 px-3 relative overflow-hidden border", status.bg, status.border, isCancelled && "opacity-55")}
        style={{
          boxShadow: "3px 4px 8px rgba(0,0,0,0.18), inset -1px -1px 3px rgba(0,0,0,0.04)",
          borderLeft: topicColor ? `3px solid ${topicColor}` : undefined,
        }}
      >
        {/* Ruled lines texture */}
        {Array.from({ length: 7 }).map((_, i) => (
          <div
            key={i}
            className="absolute left-0 right-0 h-px"
            style={{ top: `${(i + 1) * 13}%`, backgroundColor: "rgba(0,0,0,0.035)" }}
          />
        ))}

        {/* Task name */}
        <p className={cn("text-sm font-medium text-gray-800 leading-snug relative", isCancelled && "line-through")}>
          {task.name}
        </p>

        {/* Topic */}
        {topicName && (
          <p className="text-xs text-gray-500 mt-1 truncate relative">{topicName}</p>
        )}

        {/* Priority + deadline row */}
        <div className="mt-2 flex items-center gap-2 relative">
          {task.priority !== null && (
            <div className="flex gap-0.5">
              {[1, 2, 3, 4, 5].map((p) => (
                <div
                  key={p}
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ backgroundColor: p <= (task.priority ?? 0) ? "#555" : "#ccc" }}
                />
              ))}
            </div>
          )}
          {task.effective_deadline && (
            <span className="text-[11px] text-gray-500 ml-auto">{task.effective_deadline}</span>
          )}
        </div>

        {/* Tags */}
        {task.tags.length > 0 && (
          <div className="mt-1.5 flex flex-wrap gap-1 relative">
            {task.tags.slice(0, 2).map((tag) => (
              <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-black/[0.07] text-gray-600">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Column
// ---------------------------------------------------------------------------

function Column({
  status,
  tasks,
  topicMap,
}: {
  status: (typeof STATUSES)[number];
  tasks: TaskItem[];
  topicMap: Map<string, Topic>;
}) {
  return (
    <div className="flex flex-col flex-1 min-w-0 h-full">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-amber-950/25 bg-amber-950/10 flex-shrink-0">
        <div className={cn("w-2.5 h-2.5 rounded-full flex-shrink-0", status.pin)} />
        <span className="text-amber-100 font-semibold text-xs uppercase tracking-widest">{status.label}</span>
        <span className="ml-auto text-amber-200/50 text-xs font-medium">{tasks.length}</span>
      </div>

      {/* Cards */}
      <div className="flex-1 overflow-y-auto pt-6" style={{ scrollbarWidth: "none" }}>
        {tasks.length === 0 ? (
          <p className="text-amber-200/25 text-xs text-center mt-6 italic select-none">empty</p>
        ) : (
          tasks.map((task) => (
            <TaskCard key={task.id} task={task} status={status} topicMap={topicMap} />
          ))
        )}
        {/* Bottom padding so last card isn't flush against edge */}
        <div className="h-6" />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Cork board skeleton
// ---------------------------------------------------------------------------

function BoardSkeleton() {
  return (
    <div className="flex-1 bg-gradient-to-br from-amber-700 via-amber-800 to-amber-900 rounded-2xl border-[6px] border-amber-900 overflow-hidden flex">
      {STATUSES.map((s, i) => (
        <div key={s.id} className={cn("flex-1 flex flex-col", i < STATUSES.length - 1 && "border-r border-amber-950/30")}>
          <div className="px-4 py-3 border-b border-amber-950/25 bg-amber-950/10 flex items-center gap-2">
            <div className={cn("w-2.5 h-2.5 rounded-full", s.pin)} />
            <span className="text-amber-100 font-semibold text-xs uppercase tracking-widest">{s.label}</span>
          </div>
          <div className="flex-1 p-4 space-y-5">
            {i < 3 && <Skeleton className="h-20 w-full opacity-30 rounded" />}
            {i < 2 && <Skeleton className="h-16 w-full opacity-20 rounded" />}
          </div>
        </div>
      ))}
    </div>
  );
}

// ---------------------------------------------------------------------------
// TaskBoard page
// ---------------------------------------------------------------------------

export function TaskBoard() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [topicFilter, setTopicFilter] = useState("");

  useEffect(() => {
    Promise.all([fetchApi<TaskItem[]>("/tasks"), fetchApi<Topic[]>("/topics")])
      .then(([t, tp]) => { setTasks(t); setTopics(tp); })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Unknown error"))
      .finally(() => setLoading(false));
  }, []);

  const topicMap = useMemo(() => new Map(topics.map((t) => [t.id, t])), [topics]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return tasks.filter((t) => {
      if (q && !t.name.toLowerCase().includes(q)) return false;
      if (topicFilter && !t.topic_ids.includes(topicFilter)) return false;
      return true;
    });
  }, [tasks, search, topicFilter]);

  const byStatus = useMemo(() => {
    const map = new Map<string, TaskItem[]>(STATUSES.map((s) => [s.id, []]));
    filtered.forEach((t) => map.get(t.status)?.push(t));
    return map;
  }, [filtered]);

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
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground mb-1">Task Board</h1>
          <p className="text-muted-foreground text-sm">
            {loading ? "Loading…" : `${tasks.length} tasks`}
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            <input
              type="text"
              placeholder="Search tasks…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-2 text-sm bg-card border border-border rounded-lg outline-none focus:ring-2 focus:ring-sidebar-primary/40 w-48"
            />
          </div>

          {topics.length > 0 && (
            <select
              value={topicFilter}
              onChange={(e) => setTopicFilter(e.target.value)}
              className="px-3 py-2 text-sm bg-card border border-border rounded-lg outline-none focus:ring-2 focus:ring-sidebar-primary/40"
            >
              <option value="">All topics</option>
              {topics.map((tp) => (
                <option key={tp.id} value={tp.id}>{tp.name}</option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Cork board */}
      {loading ? (
        <BoardSkeleton />
      ) : (
        <div
          className="flex-1 rounded-2xl border-[6px] border-amber-900 overflow-hidden flex relative"
          style={{
            background: "linear-gradient(135deg, #92400e 0%, #78350f 40%, #6b280c 100%)",
          }}
        >
          {/* Cork texture overlay */}
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundImage: [
                "radial-gradient(circle at 18% 52%, transparent 1%, rgba(139,69,19,0.25) 1.5%, transparent 2%)",
                "radial-gradient(circle at 62% 18%, transparent 1%, rgba(139,69,19,0.25) 1.5%, transparent 2%)",
                "radial-gradient(circle at 38% 82%, transparent 1%, rgba(139,69,19,0.25) 1.5%, transparent 2%)",
                "radial-gradient(circle at 79% 65%, transparent 1%, rgba(139,69,19,0.25) 1.5%, transparent 2%)",
                "radial-gradient(circle at 45% 35%, transparent 0.5%, rgba(139,69,19,0.15) 1%, transparent 1.5%)",
              ].join(","),
              backgroundSize: "120px 120px",
              opacity: 0.6,
            }}
          />

          {/* Columns */}
          {STATUSES.map((status, i) => (
            <div
              key={status.id}
              className={cn("flex-1 flex flex-col min-w-0 relative", i < STATUSES.length - 1 && "border-r border-amber-950/35")}
            >
              <Column
                status={status}
                tasks={byStatus.get(status.id) ?? []}
                topicMap={topicMap}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
