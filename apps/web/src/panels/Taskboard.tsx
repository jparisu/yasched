import { useMemo, useState } from 'react';
import { useData } from '../store';
import { ElementDTO } from '../types';
import {
  attrBool,
  attrNumber,
  attrString,
  byType,
  byWhenAsc,
  displayName,
  isVisibleTask,
  whenOf,
} from '../lib/elements';
import { ElementView } from '../ui/ElementView';
import { ElementViewMode } from '../settings';
import { usePersistentState } from '../lib/usePersistentState';
import { today } from '../lib/format';

// ---------------------------------------------------------------------------
// Grouping model — each axis buckets tasks and (if mutable) knows how to write
// the attribute when a card is dropped into one of its buckets.
// ---------------------------------------------------------------------------

type GroupKey = 'none' | 'status' | 'priority' | 'topic' | 'focus';

interface Group {
  key: string;
  label: string;
}

interface Grouping {
  label: string;
  groups: (tasks: ElementDTO[], byId: Record<string, ElementDTO>) => Group[];
  keyOf: (t: ElementDTO) => string;
  apply?: (key: string) => Record<string, unknown>;
}

const STATUS = ['not-started', 'in-progress', 'completed', 'paused'];
const PRIORITY_VALUE: Record<string, number> = { low: 2, medium: 5, high: 9 };

function priorityBucket(p: number | undefined): string {
  const v = p ?? 0;
  if (v >= 8) return 'high';
  if (v >= 4) return 'medium';
  return 'low';
}

const GROUPINGS: Record<GroupKey, Grouping> = {
  none: {
    label: 'None',
    groups: () => [{ key: 'all', label: 'All tasks' }],
    keyOf: () => 'all',
  },
  status: {
    label: 'Status',
    groups: () => STATUS.map((s) => ({ key: s, label: s.replace('-', ' ') })),
    keyOf: (t) => attrString(t, 'status') ?? 'not-started',
    apply: (key) => ({ status: key }),
  },
  priority: {
    label: 'Priority',
    groups: () => ['high', 'medium', 'low'].map((k) => ({ key: k, label: k })),
    keyOf: (t) => priorityBucket(attrNumber(t, 'priority')),
    apply: (key) => ({ priority: PRIORITY_VALUE[key] }),
  },
  focus: {
    label: 'On-focus',
    groups: () => [
      { key: 'yes', label: 'Focused' },
      { key: 'no', label: 'Not focused' },
    ],
    keyOf: (t) => (attrBool(t, 'focus') ? 'yes' : 'no'),
    apply: (key) => ({ focus: key === 'yes' }),
  },
  topic: {
    label: 'Topic',
    groups: (tasks, byId) => {
      const seen = new Map<string, string>();
      for (const t of tasks) {
        const k = t.topic ?? 'none';
        if (!seen.has(k)) seen.set(k, k === 'none' ? '(no topic)' : displayName(byId[k]));
      }
      return [...seen].map(([key, label]) => ({ key, label }));
    },
    keyOf: (t) => t.topic ?? 'none',
  },
};

const AXES: GroupKey[] = ['status', 'priority', 'topic', 'focus', 'none'];
const VIEWS: ElementViewMode[] = ['card', 'line', 'point'];

/** Collapse generated occurrences of the same schedule into one representative:
 *  the first upcoming one (else the most recent), so scheduled tasks show once. */
function dedupeScheduled(all: ElementDTO[], byId: Record<string, ElementDTO>): ElementDTO[] {
  const now = today();
  const singles: ElementDTO[] = [];
  const groups = new Map<string, ElementDTO[]>();
  for (const t of all) {
    const gen =
      t.virtual && t.mainParent && byId[t.mainParent]?.type === 'schedule' ? t.mainParent : null;
    if (!gen) {
      singles.push(t);
    } else {
      const arr = groups.get(gen) ?? [];
      if (arr.length === 0) groups.set(gen, arr);
      arr.push(t);
    }
  }
  const reps = [...groups.values()].map((list) => {
    const future = list.filter((t) => (whenOf(t) ?? now) >= now).sort(byWhenAsc);
    if (future.length) return future[0];
    const sorted = [...list].sort(byWhenAsc);
    return sorted[sorted.length - 1] ?? list[0];
  });
  return [...singles, ...reps];
}

export function Taskboard({ onOpen }: { onOpen: (id: string) => void }) {
  const { elements, byId, patchAttributes } = useData();
  const [colDim, setColDim] = usePersistentState<GroupKey>('taskboard-cols', 'status');
  const [rowDim, setRowDim] = usePersistentState<GroupKey>('taskboard-rows', 'none');
  const [view, setView] = usePersistentState<ElementViewMode>('taskboard-view', 'card');
  const [dragId, setDragId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const tasks = useMemo(
    () => dedupeScheduled(byType(elements, 'task').filter((t) => isVisibleTask(t, byId)), byId),
    [elements, byId],
  );
  const cols = GROUPINGS[colDim].groups(tasks, byId);
  const rows = GROUPINGS[rowDim].groups(tasks, byId);

  const moveTo = async (id: string, rowKey: string, colKey: string) => {
    const patch: Record<string, unknown> = {};
    Object.assign(patch, GROUPINGS[rowDim].apply?.(rowKey) ?? {});
    Object.assign(patch, GROUPINGS[colDim].apply?.(colKey) ?? {});
    if (Object.keys(patch).length === 0) return;
    setError(null);
    try {
      await patchAttributes(id, patch);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const cellTasks = (rowKey: string, colKey: string) =>
    tasks.filter(
      (t) => GROUPINGS[rowDim].keyOf(t) === rowKey && GROUPINGS[colDim].keyOf(t) === colKey,
    );

  const hasRows = rowDim !== 'none';
  const gridTemplate = hasRows
    ? `40px repeat(${cols.length}, minmax(0, 1fr))`
    : `repeat(${cols.length}, minmax(0, 1fr))`;
  const droppable = !!(GROUPINGS[colDim].apply || GROUPINGS[rowDim].apply);

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-4">
        <AxisPicker label="Columns" value={colDim} onChange={setColDim} />
        <AxisPicker label="Rows" value={rowDim} onChange={setRowDim} />
        <label className="flex items-center gap-2 text-sm">
          <span className="text-slate-500">View</span>
          <div className="flex gap-1">
            {VIEWS.map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`px-2.5 py-1 rounded-lg border text-sm capitalize ${
                  view === v ? 'bg-sky-500 text-white border-sky-500' : 'border-slate-200 dark:border-slate-700'
                }`}
              >
                {v}
              </button>
            ))}
          </div>
        </label>
        {error && <span className="text-sm text-rose-500">{error}</span>}
      </div>

      <div className="overflow-x-auto">
        <div className="grid gap-3 min-w-[640px]" style={{ gridTemplateColumns: gridTemplate }}>
          {/* column headers */}
          {hasRows && <div />}
          {cols.map((c) => (
            <div key={`h-${c.key}`} className="px-1 text-base font-bold capitalize text-slate-700 dark:text-slate-200">
              {c.label}
            </div>
          ))}

          {/* body */}
          {rows.map((r) => (
            <RowCells
              key={`r-${r.key}`}
              row={r}
              cols={cols}
              hasRows={hasRows}
              view={view}
              droppable={droppable}
              cellTasks={cellTasks}
              onOpen={onOpen}
              dragId={dragId}
              setDragId={setDragId}
              moveTo={moveTo}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function AxisPicker({
  label,
  value,
  onChange,
}: {
  label: string;
  value: GroupKey;
  onChange: (v: GroupKey) => void;
}) {
  return (
    <label className="flex items-center gap-2 text-sm">
      <span className="text-slate-500">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as GroupKey)}
        className="px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
      >
        {AXES.map((a) => (
          <option key={a} value={a}>
            {GROUPINGS[a].label}
          </option>
        ))}
      </select>
    </label>
  );
}

function RowCells({
  row,
  cols,
  hasRows,
  view,
  droppable,
  cellTasks,
  onOpen,
  dragId,
  setDragId,
  moveTo,
}: {
  row: Group;
  cols: Group[];
  hasRows: boolean;
  view: ElementViewMode;
  droppable: boolean;
  cellTasks: (rowKey: string, colKey: string) => ElementDTO[];
  onOpen: (id: string) => void;
  dragId: string | null;
  setDragId: (id: string | null) => void;
  moveTo: (id: string, rowKey: string, colKey: string) => void;
}) {
  return (
    <>
      {hasRows && (
        <div className="flex items-center justify-center">
          <span
            className="text-base font-bold capitalize text-slate-700 dark:text-slate-200 whitespace-nowrap"
            style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)' }}
          >
            {row.label}
          </span>
        </div>
      )}
      {cols.map((c) => {
        const items = cellTasks(row.key, c.key);
        return (
          <div
            key={`${row.key}-${c.key}`}
            onDragOver={(e) => droppable && e.preventDefault()}
            onDrop={() => {
              if (dragId) moveTo(dragId, row.key, c.key);
              setDragId(null);
            }}
            className="card p-2 min-h-[90px]"
          >
            <div className={view === 'point' ? 'flex flex-wrap gap-1.5' : 'space-y-2'}>
              {items.map((t) => (
                <div
                  key={t.id}
                  draggable={droppable}
                  onDragStart={() => setDragId(t.id)}
                  onDragEnd={() => setDragId(null)}
                >
                  <ElementView element={t} mode={view} onClick={onOpen} />
                </div>
              ))}
              {items.length === 0 && <p className="text-xs text-slate-400">—</p>}
            </div>
          </div>
        );
      })}
    </>
  );
}
