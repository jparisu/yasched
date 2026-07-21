import { useEffect, useState } from 'react';
import { ChevronDown, Check } from 'lucide-react';
import { DisplayItem, GlobalControls, ZoomControls } from '../components/ui';
import { useData } from '../data/DataContext';
import { useEditor } from '../data/EditorContext';
import { useElement } from '../data/ElementContext';
import { usePanelConfig } from '../data/usePanelConfig';
import { useSettings } from '../data/SettingsContext';
import { tintRgba } from '../lib/colors';
import { itemListClass } from '../lib/itemList';
import { orderTasks } from '../lib/tasks';
import { orderTopics } from '../lib/topics';
import { levelOf } from '../lib/levels';
import { useCollapse } from '../lib/useCollapse';
import { Density, Task } from '../types';

type GroupMode = 'stage' | 'priority' | 'topic' | 'time';
interface Group {
  id: string;
  label: string;
  color?: string;
  depth?: number;
}

const MODES: { value: GroupMode; label: string }[] = [
  { value: 'stage', label: 'Stage' },
  { value: 'priority', label: 'Priority' },
  { value: 'topic', label: 'Topic' },
  { value: 'time', label: 'Time' },
];

const TOPICS_KEY = 'yasched-taskboard-topics';

export function TaskBoard() {
  const { tasks, topics } = useData();
  const { openEdit } = useEditor();
  const { openElement } = useElement();
  const { settings } = useSettings();
  const { view: displayStyle, setView, zoom, stepZoom, setZoom, config, update } =
    usePanelConfig('taskboard');
  const density = 'comfortable' as Density;
  const columnMode = config.columnMode as GroupMode;
  const rowMode = config.rowMode as GroupMode;
  const setColumnMode = (m: GroupMode) => update({ columnMode: m });
  const setRowMode = (m: GroupMode) => update({ rowMode: m });
  const resize = config.resize;

  const topicSelector = useCollapse('taskboard-topic-selector', true);

  // Topic hierarchy helpers (nest by first existing parent).
  const topicById = new Map(topics.map((t) => [t.id, t]));
  const parentOf = (id: string): string | undefined => {
    const p = topicById.get(id)?.parentIds?.[0];
    return p && topicById.has(p) ? p : undefined;
  };
  const chainOf = (id: string): string[] => {
    const out: string[] = [];
    let cur: string | undefined = id;
    const seen = new Set<string>();
    while (cur && !seen.has(cur)) {
      seen.add(cur);
      out.push(cur);
      cur = parentOf(cur);
    }
    return out; // [self, parent, grandparent, …]
  };
  const rootIds = topics.filter((t) => !parentOf(t.id)).map((t) => t.id);

  // Which topics are shown as buckets. null = default (main/root topics only).
  const [shownArr, setShownArr] = useState<string[] | null>(() => {
    try {
      const s = localStorage.getItem(TOPICS_KEY);
      return s ? (JSON.parse(s) as string[]) : null;
    } catch {
      return null;
    }
  });
  useEffect(() => {
    try {
      if (shownArr) localStorage.setItem(TOPICS_KEY, JSON.stringify(shownArr));
      else localStorage.removeItem(TOPICS_KEY);
    } catch {
      /* ignore */
    }
  }, [shownArr]);
  const shown = new Set(shownArr ?? rootIds);
  const toggleTopic = (id: string) =>
    setShownArr(() => {
      const s = new Set(shown);
      if (s.has(id)) s.delete(id);
      else s.add(id);
      return [...s];
    });

  // The most specific shown topic on a task's ancestor chain (roll-up bucket).
  const topicBucket = (task: Task): string | undefined =>
    chainOf(task.topicId ?? '').find((id) => shown.has(id));

  const groupDefs = (mode: GroupMode): Group[] => {
    switch (mode) {
      case 'stage':
        return [
          { id: 'todo', label: 'To Do', color: '#3b82f6' },
          { id: 'doing', label: 'Doing', color: '#f59e0b' },
          { id: 'done', label: 'Done', color: '#22c55e' },
        ];
      case 'priority':
        return [
          { id: 'high', label: 'High', color: '#ef4444' },
          { id: 'medium', label: 'Medium', color: '#f59e0b' },
          { id: 'low', label: 'Low', color: '#22c55e' },
        ];
      case 'topic':
        return orderTopics(topics)
          .filter(({ topic }) => shown.has(topic.id))
          .map(({ topic, depth }) => ({ id: topic.id, label: topic.name, color: topic.color, depth }));
      case 'time':
        return [
          { id: 'this_week', label: 'This Week' },
          { id: 'later', label: 'Later' },
          { id: 'none', label: 'No Deadline' },
        ];
    }
  };

  const timeBucket = (task: Task): string => {
    if (!task.deadline) return 'none';
    const weekFromNow = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
    return new Date(task.deadline) <= weekFromNow ? 'this_week' : 'later';
  };

  const matches = (task: Task, mode: GroupMode, groupId: string): boolean => {
    switch (mode) {
      case 'stage':
        return task.status === groupId;
      case 'priority':
        return levelOf(task.priority, settings.priorityRanges) === groupId;
      case 'topic':
        return topicBucket(task) === groupId;
      case 'time':
        return timeBucket(task) === groupId;
    }
  };

  const singleAxis = columnMode === rowMode;
  const columns = groupDefs(columnMode);
  const rows: Group[] = singleAxis ? [{ id: '__all__', label: 'All' }] : groupDefs(rowMode);

  const cellTasks = (colId: string, rowId: string) =>
    tasks.filter(
      (t) => matches(t, columnMode, colId) && (rowId === '__all__' || matches(t, rowMode, rowId))
    );

  const cellPad = density === 'expanded' ? 'p-3' : density === 'comfortable' ? 'p-2' : 'p-1.5';
  const topicMode = columnMode === 'topic' || rowMode === 'topic';

  const ModeSelector = ({
    label,
    value,
    onChange,
  }: {
    label: string;
    value: GroupMode;
    onChange: (m: GroupMode) => void;
  }) => (
    <div className="flex items-center gap-2">
      <span className="text-xs text-slate-500 dark:text-slate-400">{label}:</span>
      <div className="flex items-center gap-0.5 p-0.5 bg-slate-100 dark:bg-slate-800 rounded-lg">
        {MODES.map((m) => (
          <button
            key={m.value}
            onClick={() => onChange(m.value)}
            className={`px-2.5 py-1 text-xs rounded-md transition-all ${
              value === m.value
                ? 'bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-4 flex-wrap">
          <ModeSelector label="Columns" value={columnMode} onChange={setColumnMode} />
          <ModeSelector label="Rows" value={rowMode} onChange={setRowMode} />
        </div>
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 dark:text-slate-400">Resize:</span>
            <button
              onClick={() => update({ resize: !resize })}
              className={`px-2.5 py-1 text-xs rounded-md font-medium transition-all ${
                resize ? 'bg-sky-500 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
              }`}
              title={resize ? 'Cells grow with content' : 'Cells are fixed size (scroll)'}
            >
              {resize ? 'On' : 'Off'}
            </button>
          </div>
          <GlobalControls displayStyle={displayStyle} onDisplayStyleChange={setView} />
          <ZoomControls zoom={zoom} onStep={stepZoom} onReset={() => setZoom(1)} />
        </div>
      </div>

      {/* Topic selector — pick which topics/sub-topics become buckets. */}
      {topicMode && (
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="flex items-center justify-between px-3 py-2">
            <button onClick={topicSelector.toggle} className="flex items-center gap-1.5 text-sm font-medium text-slate-600 dark:text-slate-300">
              <ChevronDown size={15} className={`transition-transform ${topicSelector.collapsed ? '-rotate-90' : ''}`} />
              Topics shown ({shown.size})
            </button>
            <div className="flex items-center gap-2 text-xs">
              <button onClick={() => setShownArr(null)} className="px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-700 dark:hover:text-slate-200">
                Main topics
              </button>
              <button onClick={() => setShownArr(topics.map((t) => t.id))} className="px-2 py-1 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-700 dark:hover:text-slate-200">
                All
              </button>
            </div>
          </div>
          {!topicSelector.collapsed && (
            <div className="px-3 pb-3 flex flex-wrap gap-1.5">
              {orderTopics(topics).map(({ topic, depth }) => {
                const on = shown.has(topic.id);
                return (
                  <button
                    key={topic.id}
                    onClick={() => toggleTopic(topic.id)}
                    style={{ marginLeft: depth * 14, backgroundColor: on ? topic.color : undefined }}
                    className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border transition-colors ${
                      on
                        ? 'border-transparent text-white'
                        : 'border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 line-through'
                    }`}
                  >
                    {on && <Check size={11} />}
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: on ? 'rgba(255,255,255,0.9)' : topic.color }} />
                    {topic.name}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}

      <div
        className="board-surface overflow-auto rounded-2xl shadow-lg border border-slate-200/50 dark:border-slate-700 bg-white dark:bg-slate-800"
        style={{ maxHeight: 'calc(100vh - 12rem)' }}
      >
        <table className={`w-full border-collapse min-w-[600px] ${resize ? '' : 'table-fixed'}`} style={{ zoom }}>
          <thead>
            <tr>
              {!singleAxis && (
                <th className="w-32 p-3 border-b border-r border-slate-200/50 dark:border-slate-700 text-left">
                  <span className="text-xs font-medium text-slate-400">
                    {MODES.find((m) => m.value === rowMode)?.label} · {MODES.find((m) => m.value === columnMode)?.label}
                  </span>
                </th>
              )}
              {columns.map((col) => (
                <th
                  key={col.id}
                  className="p-3 border-b border-r border-slate-200/50 dark:border-slate-700"
                  style={{ backgroundColor: col.color ? tintRgba(col.color, 0.14) : undefined }}
                >
                  <div className="flex items-center gap-2" style={{ paddingLeft: (col.depth ?? 0) * 12 }}>
                    {col.color && <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: col.color }} />}
                    <span className="font-semibold text-slate-700 dark:text-slate-200 truncate">{col.label}</span>
                    {columnMode === 'topic' && (
                      <button
                        onClick={() => toggleTopic(col.id)}
                        title="Hide this topic"
                        className="ml-1 text-slate-400 hover:text-coral-500 text-xs"
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                {!singleAxis && (
                  <td className="p-3 border-r border-b border-slate-200/50 dark:border-slate-700 align-top" style={{ backgroundColor: row.color ? tintRgba(row.color, 0.1) : undefined }}>
                    <span className="font-medium text-slate-700 dark:text-slate-200 text-sm" style={{ paddingLeft: (row.depth ?? 0) * 12 }}>
                      {row.label}
                    </span>
                  </td>
                )}
                {columns.map((col) => {
                  const cellItems = orderTasks(cellTasks(col.id, row.id));
                  return (
                    <td key={col.id} className={`${cellPad} border-r border-b border-slate-200/50 dark:border-slate-700 align-top`}>
                      <div className={`${itemListClass(displayStyle)} ${resize ? '' : 'h-56 overflow-y-auto pr-1'}`}>
                        {cellItems.map(({ task, depth }) => (
                          <DisplayItem
                            key={task.id}
                            title={task.title}
                            description={task.description}
                            displayStyle={displayStyle}
                            itemStyle={task.style}
                            topicId={task.topicId}
                            priority={task.priority}
                            status={task.status}
                            deadline={task.deadline}
                            depth={depth}
                            onClick={() => openEdit('tasks', task.id)}
                            onDoubleClick={() => openElement('tasks', task.id)}
                          />
                        ))}
                        {cellItems.length === 0 && (
                          <div className="text-xs text-slate-300 dark:text-slate-600 text-center py-3">—</div>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
