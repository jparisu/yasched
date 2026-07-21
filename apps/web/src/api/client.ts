import { Task, EventItem, Deadline, Topic } from '../types';

export interface AgendaData {
  topics: Topic[];
  tasks: Task[];
  events: EventItem[];
  deadlines: Deadline[];
}

export interface ValidationIssue {
  severity: 'error' | 'warning';
  code: string;
  message: string;
  entityKind: string;
  entityId: string;
}

export interface ValidationResult {
  issues: ValidationIssue[];
  errorCount: number;
  warningCount: number;
}

export interface RefItem {
  id: string;
  name: string;
}

export interface Meta {
  agenda: string;
  readOnly: boolean;
  traits: string[];
  topics: RefItem[];
  tasks: RefItem[];
  events: RefItem[];
}

export type EntityKind = 'topics' | 'tasks' | 'events';

export interface GraphTopic {
  id: string;
  name: string;
  color: string;
  parentIds: string[];
}
export interface GraphNode {
  id: string;
  kind: 'task' | 'event';
  label: string;
  topicId: string | null;
  topicIds: string[];
  tags: string[];
}
export interface GraphEdge {
  source: string;
  target: string;
  type: string;
}
export interface GraphData {
  topics: GraphTopic[];
  nodes: GraphNode[];
  edges: GraphEdge[];
  topicEdges: GraphEdge[];
}

export interface TimetableEntry {
  id: string;
  eventId: string;
  title: string;
  weekday: number; // 0 = Monday .. 6 = Sunday
  startTime: string | null;
  endTime: string | null;
  topicId: string;
  location: string | null;
  style: { backgroundColor: string; leftColor: string; shape: string };
}

// A raw entity spec matching the YAML entity shape (used for create/update).
export type EntitySpec = Record<string, unknown>;

// ---------------------------------------------------------------------------

// View ids may be suffixed (event occurrence `id::date`, deadline `id::deadline`).
// The underlying entity id is the part before the first "::".
export const baseId = (viewId: string): string => viewId.split('::')[0];

const API_BASE = '/api';

type RawTask = Omit<Task, 'deadline' | 'startDate' | 'createdAt'> & {
  deadline: string | null;
  createdAt: string;
};
type RawEvent = Omit<EventItem, 'date'> & { date: string };
type RawDeadline = Omit<Deadline, 'date'> & { date: string };
interface RawAgenda {
  topics: Topic[];
  tasks: RawTask[];
  events: RawEvent[];
  deadlines: RawDeadline[];
}

function parseLocalDate(value: string): Date {
  const parts = value.split('-').map(Number);
  if (parts.length === 3 && parts.every((n) => !Number.isNaN(n))) {
    return new Date(parts[0], parts[1] - 1, parts[2]);
  }
  return new Date(value);
}

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`Request failed: ${path} (HTTP ${res.status})`);
  return (await res.json()) as T;
}

export async function fetchAgenda(): Promise<AgendaData> {
  const raw = await getJSON<RawAgenda>('/agenda');
  return {
    topics: raw.topics,
    tasks: raw.tasks.map((t) => ({
      ...t,
      deadline: t.deadline ? parseLocalDate(t.deadline) : undefined,
      createdAt: t.createdAt ? parseLocalDate(t.createdAt) : new Date(),
    })),
    events: raw.events.map((e) => ({ ...e, date: parseLocalDate(e.date) })),
    deadlines: raw.deadlines.map((d) => ({ ...d, date: parseLocalDate(d.date) })),
  };
}

/** Dated event occurrences within an inclusive [start, end] date window (ISO). */
export async function fetchEventsRange(start: string, end: string): Promise<EventItem[]> {
  const raw = await getJSON<RawEvent[]>(`/events?start=${start}&end=${end}`);
  return raw.map((e) => ({ ...e, date: parseLocalDate(e.date) }));
}

export const fetchValidation = (): Promise<ValidationResult> =>
  getJSON<ValidationResult>('/validate');
export const fetchMeta = (): Promise<Meta> => getJSON<Meta>('/meta');
export const fetchGraph = (): Promise<GraphData> => getJSON<GraphData>('/graph');
export const fetchTimetable = (): Promise<TimetableEntry[]> =>
  getJSON<TimetableEntry[]>('/timetable');

async function writeRequest(method: string, path: string, body?: unknown): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      if (data?.detail) detail = String(data.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
}

export const fetchEntity = (kind: EntityKind, id: string): Promise<EntitySpec> =>
  getJSON<EntitySpec>(`/${kind}/${encodeURIComponent(id)}`);

export const createEntity = (kind: EntityKind, spec: EntitySpec): Promise<void> =>
  writeRequest('POST', `/${kind}`, spec);
export const updateEntity = (kind: EntityKind, id: string, spec: EntitySpec): Promise<void> =>
  writeRequest('PUT', `/${kind}/${encodeURIComponent(id)}`, spec);
export const deleteEntity = (kind: EntityKind, id: string): Promise<void> =>
  writeRequest('DELETE', `/${kind}/${encodeURIComponent(id)}`);
