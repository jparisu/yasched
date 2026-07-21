import { useEffect, useState, ReactNode } from 'react';
import { Pencil, ListTodo, CalendarPlus, FolderOpen, Share2, ChevronDown } from 'lucide-react';
import { useCollapse } from '../../lib/useCollapse';
import {
  EntityKind,
  EntitySpec,
  GraphData,
  fetchEntity,
  fetchGraph,
} from '../../api/client';
import { useData } from '../../data/DataContext';
import { useEditor } from '../../data/EditorContext';
import { EntityGraph } from '../ui/EntityGraph';
import { DisplayItem } from '../ui/DisplayItem';
import { Task } from '../../types';

interface Props {
  kind: EntityKind;
  entityId: string;
  onNavigate: (kind: EntityKind, id: string) => void;
}

const KIND_META: Record<EntityKind, { label: string; icon: ReactNode; color: string }> = {
  topics: { label: 'Topic', icon: <FolderOpen size={18} />, color: '#0ea5e9' },
  tasks: { label: 'Task', icon: <ListTodo size={18} />, color: '#8b5cf6' },
  events: { label: 'Event', icon: <CalendarPlus size={18} />, color: '#14b8a6' },
};

/** A collapsible titled block inside the element detail. */
function DetailSection({ title, children }: { title: string; children: ReactNode }) {
  const { collapsed, toggle } = useCollapse(`element-section-${title}`);
  return (
    <div className="space-y-1.5">
      <button
        onClick={toggle}
        className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wide text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
      >
        <ChevronDown size={12} className={`transition-transform ${collapsed ? '-rotate-90' : ''}`} />
        {title}
      </button>
      {!collapsed && children}
    </div>
  );
}

const asStr = (v: unknown) => (v === null || v === undefined ? '' : String(v));
const asArr = (v: unknown): string[] => (Array.isArray(v) ? v.map(String) : v ? [String(v)] : []);
const isRec = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);

function formatSchedule(raw: Record<string, unknown>): string {
  const type = asStr(raw.type);
  const time = raw.start_time
    ? ` at ${asStr(raw.start_time)}${raw.end_time ? `–${asStr(raw.end_time)}` : raw.duration ? ` for ${asStr(raw.duration)}` : ''}`
    : '';
  const bounds =
    raw.start_date || raw.end_date
      ? `  (${asStr(raw.start_date) || '…'} → ${asStr(raw.end_date) || '…'})`
      : '';
  let base = type;
  if (type === 'weekly') base = `Weekly on ${asArr(raw.week_days).join(', ') || '—'}`;
  else if (type === 'monthly') base = `Monthly on day ${asStr(raw.day)}`;
  else if (type === 'yearly') base = `Yearly on ${asStr(raw.month)}/${asStr(raw.day)}`;
  else if (type === 'single_day') base = `On ${asStr(raw.day)}`;
  else if (type === 'multi_day') base = `${asStr(raw.start_day)} → ${asStr(raw.end_day)}`;
  return base + time + bounds;
}

export function ElementDetail({ kind, entityId, onNavigate }: Props) {
  const { topics, tasks, meta } = useData();
  const { openEdit } = useEditor();
  const [raw, setRaw] = useState<EntitySpec | null>(null);
  const [graph, setGraph] = useState<GraphData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setRaw(null);
    setError(null);
    fetchEntity(kind, entityId)
      .then(setRaw)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, [kind, entityId]);

  useEffect(() => {
    fetchGraph().then(setGraph);
  }, []);

  const nameOf = (arr: { id: string; name: string }[] | undefined, id: string) =>
    arr?.find((x) => x.id === id)?.name ?? id;
  const topicName = (id: string) => nameOf(meta?.topics, id);
  const taskName = (id: string) => nameOf(meta?.tasks, id);
  const eventName = (id: string) => nameOf(meta?.events, id);

  const km = KIND_META[kind];
  const name = raw ? asStr(raw.name) || entityId : entityId;
  const color = (kind === 'topics' && topics.find((t) => t.id === entityId)?.color) || km.color;

  const subtopics = graph?.topics.filter((t) => t.parentIds.includes(entityId)) ?? [];
  const memberNodes = graph?.nodes.filter((n) => n.topicId === entityId) ?? [];

  // Sub-task tree (all descendants, regardless of on-focus).
  const taskTree: { task: Task; depth: number }[] = [];
  if (kind === 'tasks') {
    const childrenOf = new Map<string, Task[]>();
    for (const t of tasks) {
      if (t.parentId) {
        const l = childrenOf.get(t.parentId) ?? [];
        l.push(t);
        childrenOf.set(t.parentId, l);
      }
    }
    const walk = (id: string, depth: number, seen: Set<string>) => {
      if (seen.has(id)) return;
      seen.add(id);
      const t = tasks.find((x) => x.id === id);
      if (t) taskTree.push({ task: t, depth });
      for (const c of childrenOf.get(id) ?? []) walk(c.id, depth + 1, seen);
    };
    walk(entityId, 0, new Set());
  }

  const childByParent =
    graph?.edges.filter(
      (e) => e.target === entityId && (e.type === 'subtask' || e.type === 'suboccurrence')
    ) ?? [];

  const Row = ({ label, value }: { label: string; value: ReactNode }) =>
    value ? (
      <div className="flex gap-2 text-sm">
        <span className="text-slate-400 w-28 flex-shrink-0">{label}</span>
        <span className="text-slate-700 dark:text-slate-200 min-w-0">{value}</span>
      </div>
    ) : null;
  const Chip = ({ children, onClick }: { children: ReactNode; onClick?: () => void }) => (
    <button
      onClick={onClick}
      className={`px-2 py-0.5 rounded-full text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 ${onClick ? 'hover:border-sky-400' : 'cursor-default'}`}
    >
      {children}
    </button>
  );

  const attrs = raw && isRec(raw.attributes) ? raw.attributes : {};
  const relations = raw && Array.isArray(raw.relations) ? raw.relations.filter(isRec) : [];
  const eventLinks = raw && Array.isArray(raw.event_links) ? raw.event_links.filter(isRec) : [];
  const schedules = raw && Array.isArray(raw.schedules) ? raw.schedules.filter(isRec) : [];
  const topicIds = raw ? asArr(raw.topic_ids) : [];
  const parentIds = raw ? asArr(raw.parent_ids) : [];
  const parentId = raw ? asStr(raw.parent_id) : '';
  const tags = raw ? asArr(raw.tags) : [];
  const traits = raw ? asArr(raw.traits) : [];

  if (error) return <div className="py-16 text-center text-coral-500">{error}</div>;
  if (!raw) return <div className="py-16 text-center text-slate-400">Loading…</div>;

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
      {/* header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-3 min-w-0">
          <span
            className="w-10 h-10 rounded-xl flex items-center justify-center text-white flex-shrink-0"
            style={{ backgroundColor: color }}
          >
            {km.icon}
          </span>
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-wide" style={{ color }}>
              {km.label}
            </p>
            <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 truncate">{name}</h2>
          </div>
        </div>
        <button
          onClick={() => openEdit(kind, entityId)}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium bg-sky-500 text-white hover:bg-sky-600 flex-shrink-0"
        >
          <Pencil size={15} /> Edit
        </button>
      </div>

      <div className="p-5 space-y-6">
        {/* details */}
        <div className="grid md:grid-cols-2 gap-5">
          <DetailSection title="Details">
            <div className="space-y-1.5">
              <Row label="Id" value={<code className="text-xs">{entityId}</code>} />
              {asStr(raw.description) && <Row label="Description" value={asStr(raw.description)} />}
              {kind === 'tasks' && <Row label="Status" value={asStr(attrs.status)} />}
              {kind === 'tasks' && <Row label="Priority" value={asStr(attrs.priority)} />}
              {kind === 'tasks' && <Row label="Deadline" value={asStr(attrs.deadline)} />}
              {kind !== 'topics' && attrs['on-focus'] != null && (
                <Row label="On-focus" value={asStr(attrs['on-focus'])} />
              )}
              {kind === 'events' && <Row label="Location" value={asStr(attrs.location)} />}
              {kind !== 'topics' && parentId && (
                <Row
                  label={kind === 'tasks' ? 'Parent task' : 'Parent event'}
                  value={
                    <Chip onClick={() => onNavigate(kind, parentId)}>
                      {kind === 'tasks' ? taskName(parentId) : eventName(parentId)}
                    </Chip>
                  }
                />
              )}
            </div>
          </DetailSection>

          <DetailSection title="Relationships">
            <div className="space-y-2">
              {kind !== 'topics' && topicIds.length > 0 && (
                <Row
                  label="Topics"
                  value={
                    <span className="flex flex-wrap gap-1">
                      {topicIds.map((t) => (
                        <Chip key={t} onClick={() => onNavigate('topics', t)}>{topicName(t)}</Chip>
                      ))}
                    </span>
                  }
                />
              )}
              {kind === 'topics' && parentIds.length > 0 && (
                <Row
                  label="Parent topics"
                  value={
                    <span className="flex flex-wrap gap-1">
                      {parentIds.map((t) => (
                        <Chip key={t} onClick={() => onNavigate('topics', t)}>{topicName(t)}</Chip>
                      ))}
                    </span>
                  }
                />
              )}
              {kind === 'topics' && subtopics.length > 0 && (
                <Row
                  label="Sub-topics"
                  value={
                    <span className="flex flex-wrap gap-1">
                      {subtopics.map((t) => (
                        <Chip key={t.id} onClick={() => onNavigate('topics', t.id)}>{t.name}</Chip>
                      ))}
                    </span>
                  }
                />
              )}
              {kind === 'topics' && memberNodes.length > 0 && (
                <Row
                  label="Contains"
                  value={
                    <span className="flex flex-wrap gap-1">
                      {memberNodes.map((n) => (
                        <Chip
                          key={n.id}
                          onClick={() => onNavigate(n.kind === 'task' ? 'tasks' : 'events', n.id)}
                        >
                          {n.kind === 'task' ? '▭' : '◆'} {n.label}
                        </Chip>
                      ))}
                    </span>
                  }
                />
              )}
              {childByParent.length > 0 && (
                <Row
                  label={kind === 'tasks' ? 'Sub-tasks' : 'Sub-events'}
                  value={
                    <span className="flex flex-wrap gap-1">
                      {childByParent.map((e) => (
                        <Chip key={e.source} onClick={() => onNavigate(kind, e.source)}>
                          {kind === 'tasks' ? taskName(e.source) : eventName(e.source)}
                        </Chip>
                      ))}
                    </span>
                  }
                />
              )}
              {relations.length > 0 && (
                <Row
                  label="Relations"
                  value={
                    <span className="flex flex-col gap-1">
                      {relations.map((r, i) => (
                        <span key={i} className="text-xs">
                          <span className="text-slate-400">{asStr(r.type)} → </span>
                          <button className="hover:text-sky-500" onClick={() => onNavigate('tasks', asStr(r.task))}>
                            {taskName(asStr(r.task))}
                          </button>
                        </span>
                      ))}
                    </span>
                  }
                />
              )}
              {eventLinks.length > 0 && (
                <Row
                  label="Event links"
                  value={
                    <span className="flex flex-wrap gap-1">
                      {eventLinks.map((l, i) => (
                        <Chip key={i} onClick={() => onNavigate('events', asStr(l.event))}>
                          {eventName(asStr(l.event))}
                          {l.use_as_deadline ? ' ⏰' : ''}
                        </Chip>
                      ))}
                    </span>
                  }
                />
              )}
              {(tags.length > 0 || traits.length > 0) && (
                <Row
                  label="Tags / traits"
                  value={
                    <span className="flex flex-wrap gap-1">
                      {tags.map((t) => <Chip key={`tag-${t}`}>#{t}</Chip>)}
                      {traits.map((t) => <Chip key={`tr-${t}`}>◈ {t}</Chip>)}
                    </span>
                  }
                />
              )}
            </div>
          </DetailSection>
        </div>

        {schedules.length > 0 && (
          <DetailSection title="Schedules">
            <ul className="space-y-1 text-sm text-slate-700 dark:text-slate-200">
              {schedules.map((s, i) => (
                <li key={i} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-500" />
                  {formatSchedule(s)}
                </li>
              ))}
            </ul>
          </DetailSection>
        )}

        {Object.keys(attrs).length > 0 && (
          <DetailSection title="All attributes">
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(attrs).map(([k, v]) => (
                <span
                  key={k}
                  className="px-2 py-0.5 rounded-md text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                >
                  <span className="text-slate-400">{k}:</span>{' '}
                  {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                </span>
              ))}
            </div>
          </DetailSection>
        )}

        {/* type-specific visualization */}
        {kind === 'topics' && (
          <DetailSection title="Topic map">
            <p className="text-xs text-slate-400 -mt-1 mb-2 flex items-center gap-1">
              <Share2 size={12} /> This topic, its sub-topics and their tasks/events.
              Double-click a node to open it here.
            </p>
            {graph ? (
              <EntityGraph
                graph={graph}
                focusId={entityId}
                onOpenEntity={openEdit}
                onOpenElement={onNavigate}
                maxHeight="46vh"
              />
            ) : (
              <div className="py-10 text-center text-slate-400">Loading…</div>
            )}
          </DetailSection>
        )}

        {kind === 'tasks' && (
          <DetailSection title="Sub-task tree">
            {taskTree.length <= 1 ? (
              <p className="text-sm text-slate-400">This task has no sub-tasks.</p>
            ) : (
              <div className="space-y-1.5">
                {taskTree.map(({ task: t, depth }) => (
                  <DisplayItem
                    key={t.id}
                    title={t.title}
                    displayStyle="line"
                    itemStyle={t.style}
                    priority={t.priority}
                    status={t.status}
                    deadline={t.deadline}
                    depth={depth}
                    onClick={() => openEdit('tasks', t.id)}
                    onDoubleClick={() => onNavigate('tasks', t.id)}
                  />
                ))}
              </div>
            )}
          </DetailSection>
        )}
      </div>
    </div>
  );
}
