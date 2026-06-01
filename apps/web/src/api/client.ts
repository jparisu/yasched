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
