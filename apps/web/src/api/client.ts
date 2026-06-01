const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

export async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export interface HealthData {
  db_loaded: boolean;
  task_count: number;
  event_count: number;
  topic_count: number;
  status_summary: {
    todo: number;
    in_progress: number;
    done: number;
    cancelled: number;
    blocked: number;
  };
  errors: string[];
}

export interface Topic {
  id: string;
  name: string;
  description: string | null;
  tags: string[];
  parent_ids: string[];
  children_ids: string[];
  effective_layout: {
    backgrounds: Array<{ type: string; color: string }>;
  } | null;
}

// ---------------------------------------------------------------------------
// Schedule discriminated union (matches API ScheduleSchema)
// ---------------------------------------------------------------------------

export type Schedule =
  | { type: "single_day"; day: string; start_time?: string | null; duration?: string | null }
  | { type: "multi_day"; start_day: string; end_day: string }
  | { type: "weekly"; appointments: { week_day: string; start_time: string; end_time?: string | null; duration?: string | null }[]; start_date?: string | null; end_date?: string | null }
  | { type: "monthly"; day_of_month: number; start_time: string; duration: string; start_date?: string | null; end_date?: string | null }
  | { type: "yearly"; month: number; day: number };

type EffectiveLayout = { backgrounds: Array<{ type: string; color: string }> } | null;

// ---------------------------------------------------------------------------
// Task and Event (used in schedule views)
// ---------------------------------------------------------------------------

export interface TaskItem {
  id: string;
  name: string;
  description: string | null;
  status: string;
  priority: number | null;
  tags: string[];
  effective_deadline: string | null;
  topic_ids: string[];
  schedules: Schedule[];
  effective_layout: EffectiveLayout;
}

export interface EventItem {
  id: string;
  name: string;
  description: string | null;
  location: string | null;
  topic_id: string;
  blocking_level: number | null;
  schedules: Schedule[];
  effective_layout: EffectiveLayout;
}

// ---------------------------------------------------------------------------
// Schedule views
// ---------------------------------------------------------------------------

export interface DailyView {
  date: string;
  events: EventItem[];
  tasks: TaskItem[];
  conflicts: { blocker_id: string; blocked_id: string; date: string }[];
}

export interface WeeklyView {
  week_start: string;
  days: DailyView[];
}
