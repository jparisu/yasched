import { useEffect, useMemo, useState } from 'react';
import { ChevronRight, ChevronsDownUp, ChevronsUpDown } from 'lucide-react';
import { useData } from '../store';
import { useSettings } from '../settings';
import { fetchEffort } from '../api';
import { EffortDTO, ElementDTO, TopicEffort } from '../types';
import { EMPTY_EFFORT, EffortMetric, EffortScope, effortParts, metricValue } from '../lib/effort';
import { ALL_TOPIC_ID, byType, displayName, subTopics } from '../lib/elements';
import { addDays, formatMinutes, isoDate, startOfWeek, today } from '../lib/format';
import { usePersistentState } from '../lib/usePersistentState';
import { PanelCard } from '../ui/PanelCard';

const METRICS: { key: EffortMetric; label: string; bar: string }[] = [
  { key: 'total', label: 'Total', bar: 'bg-sky-500' },
  { key: 'events', label: 'Events', bar: 'bg-mint-500' },
  { key: 'tasks', label: 'Tasks', bar: 'bg-lavender-500' },
];
const SCOPES: { key: EffortScope; label: string; hint: string }[] = [
  { key: 'rolled', label: 'With subtopics', hint: 'Include time from all descendant subtopics' },
  { key: 'own', label: 'Own only', hint: 'Only elements directly in the topic, not under subtopics' },
];

type Preset =
  | 'up-to-today'
  | 'all-time'
  | 'this-week'
  | 'last-week'
  | 'next-week'
  | 'this-month'
  | 'last-month'
  | 'next-month'
  | 'custom';

const PRESET_LABELS: Record<Preset, string> = {
  'up-to-today': 'Up to today',
  'all-time': 'All time',
  'this-week': 'This week',
  'last-week': 'Last week',
  'next-week': 'Next week',
  'this-month': 'This month',
  'last-month': 'Last month',
  'next-month': 'Next month',
  custom: 'Custom',
};

interface Period {
  preset: Preset;
  start: string;
  end: string;
}

function presetRange(preset: Preset, mondayStart: boolean): { start: string; end: string } {
  const t = today();
  const monthStart = (y: number, m: number) => new Date(y, m, 1);
  const monthEnd = (y: number, m: number) => new Date(y, m + 1, 0);
  switch (preset) {
    case 'all-time':
      return { start: '', end: isoDate(addDays(t, 730)) };
    case 'this-week': {
      const s = startOfWeek(t, mondayStart);
      return { start: isoDate(s), end: isoDate(addDays(s, 6)) };
    }
    case 'last-week': {
      const s = addDays(startOfWeek(t, mondayStart), -7);
      return { start: isoDate(s), end: isoDate(addDays(s, 6)) };
    }
    case 'next-week': {
      const s = addDays(startOfWeek(t, mondayStart), 7);
      return { start: isoDate(s), end: isoDate(addDays(s, 6)) };
    }
    case 'this-month':
      return { start: isoDate(monthStart(t.getFullYear(), t.getMonth())), end: isoDate(monthEnd(t.getFullYear(), t.getMonth())) };
    case 'last-month':
      return { start: isoDate(monthStart(t.getFullYear(), t.getMonth() - 1)), end: isoDate(monthEnd(t.getFullYear(), t.getMonth() - 1)) };
    case 'next-month':
      return { start: isoDate(monthStart(t.getFullYear(), t.getMonth() + 1)), end: isoDate(monthEnd(t.getFullYear(), t.getMonth() + 1)) };
    case 'up-to-today':
    default:
      return { start: '', end: isoDate(t) };
  }
}

export function Effort({ onOpen }: { onOpen: (id: string) => void }) {
  const { elements } = useData();
  const { settings } = useSettings();
  const [metric, setMetric] = usePersistentState<EffortMetric>('effort-metric', 'total');
  const [scope, setScope] = usePersistentState<EffortScope>('effort-scope', 'rolled');
  const [period, setPeriod] = usePersistentState<Period>('effort-period', {
    preset: 'up-to-today',
    start: '',
    end: isoDate(today()),
  });
  const [data, setData] = useState<EffortDTO | null>(null);
  const [loading, setLoading] = useState(false);
  const [closed, setClosed] = useState<Set<string>>(new Set());

  const range =
    period.preset === 'custom'
      ? { start: period.start, end: period.end }
      : presetRange(period.preset, settings.weekStartsOnMonday);

  useEffect(() => {
    let alive = true;
    setLoading(true);
    fetchEffort(range.start || undefined, range.end || undefined)
      .then((d) => alive && setData(d))
      .catch(() => alive && setData(null))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, [range.start, range.end, elements]);

  const topicsEffort = data?.topics ?? {};
  const eff = (id: string): TopicEffort => topicsEffort[id] ?? EMPTY_EFFORT;
  const rootValue = metricValue(eff(ALL_TOPIC_ID), metric, scope);
  const allTopicIds = useMemo(() => byType(elements, 'topic').map((t) => t.id), [elements]);

  const ranking = byType(elements, 'topic')
    .filter((t) => t.id !== ALL_TOPIC_ID)
    .map((t) => ({ id: t.id, name: displayName(t), value: metricValue(eff(t.id), metric, scope) }))
    .filter((r) => r.value > 0)
    .sort((a, b) => b.value - a.value);
  const rankMax = ranking[0]?.value ?? 0;
  const rankBar = METRICS.find((m) => m.key === metric)?.bar ?? 'bg-sky-500';

  const setPreset = (p: Preset) =>
    setPeriod(p === 'custom' ? { ...period, preset: 'custom' } : { preset: p, ...presetRange(p, settings.weekStartsOnMonday) });

  return (
    <div className="space-y-4">
      {/* Shared controls — apply to both blocks */}
      <div className="flex flex-wrap items-center gap-x-5 gap-y-3">
        <Group label="Show">
          {METRICS.map((m) => (
            <Toggle key={m.key} active={metric === m.key} onClick={() => setMetric(m.key)} label={m.label} />
          ))}
        </Group>
        <Group label="Scope">
          {SCOPES.map((s) => (
            <Toggle key={s.key} active={scope === s.key} onClick={() => setScope(s.key)} label={s.label} title={s.hint} />
          ))}
        </Group>
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-500">Period</span>
          <select
            value={period.preset}
            onChange={(e) => setPreset(e.target.value as Preset)}
            className="px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm"
          >
            {(Object.keys(PRESET_LABELS) as Preset[]).map((p) => (
              <option key={p} value={p}>
                {PRESET_LABELS[p]}
              </option>
            ))}
          </select>
          <input
            type="date"
            value={range.start}
            onChange={(e) => setPeriod({ preset: 'custom', start: e.target.value, end: range.end })}
            title="Start (empty = from the beginning)"
            className="px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm"
          />
          <span className="text-slate-400">→</span>
          <input
            type="date"
            value={range.end}
            onChange={(e) => setPeriod({ preset: 'custom', start: range.start, end: e.target.value })}
            className="px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm"
          />
        </div>
        {loading && <span className="text-xs text-slate-400">updating…</span>}
      </div>

      {/* Block 1 — time-used tree */}
      <PanelCard
        title="Time used by topic"
        collapseId="effort-tree"
        action={
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-xs text-slate-500">
              <span className="w-3 h-3 rounded-sm bg-mint-500" /> events
              <span className="w-3 h-3 rounded-sm bg-lavender-500 ml-2" /> tasks
            </span>
            <button onClick={() => setClosed(new Set(allTopicIds))} title="Collapse all" className="p-1 rounded text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
              <ChevronsDownUp size={15} />
            </button>
            <button onClick={() => setClosed(new Set())} title="Expand all" className="p-1 rounded text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">
              <ChevronsUpDown size={15} />
            </button>
          </div>
        }
      >
        {rootValue <= 0 ? (
          <p className="text-sm text-slate-400">No time recorded for this period.</p>
        ) : (
          <ul className="space-y-0.5">
            <EffortRow
              topicId={ALL_TOPIC_ID}
              depth={0}
              elements={elements}
              eff={eff}
              metric={metric}
              scope={scope}
              rootValue={rootValue}
              closed={closed}
              onToggle={(id) =>
                setClosed((prev) => {
                  const next = new Set(prev);
                  if (next.has(id)) next.delete(id);
                  else next.add(id);
                  return next;
                })
              }
              onOpen={onOpen}
            />
          </ul>
        )}
      </PanelCard>

      {/* Block 2 — ranking */}
      <PanelCard title="Topics ranked by time used" collapseId="effort-rank">
        {ranking.length === 0 ? (
          <p className="text-sm text-slate-400">No time recorded for this selection.</p>
        ) : (
          <ol className="space-y-2">
            {ranking.map((r, i) => (
              <li key={r.id} className="flex items-center gap-3">
                <span className="w-5 text-right text-xs text-slate-400 tabular-nums">{i + 1}</span>
                <button
                  onClick={() => onOpen(r.id)}
                  className="w-40 truncate text-left text-sm font-medium text-slate-700 dark:text-slate-200 hover:text-sky-600 dark:hover:text-sky-400 hover:underline"
                >
                  {r.name}
                </button>
                <div className="flex-1 h-3 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
                  <div className={`h-full ${rankBar}`} style={{ width: `${rankMax ? (r.value / rankMax) * 100 : 0}%` }} />
                </div>
                <span className="w-20 text-right text-sm tabular-nums text-slate-600 dark:text-slate-300">
                  {formatMinutes(r.value)}
                </span>
              </li>
            ))}
          </ol>
        )}
      </PanelCard>
    </div>
  );
}

function EffortRow({
  topicId,
  depth,
  elements,
  eff,
  metric,
  scope,
  rootValue,
  closed,
  onToggle,
  onOpen,
}: {
  topicId: string;
  depth: number;
  elements: ElementDTO[];
  eff: (id: string) => TopicEffort;
  metric: EffortMetric;
  scope: EffortScope;
  rootValue: number;
  closed: Set<string>;
  onToggle: (id: string) => void;
  onOpen: (id: string) => void;
}) {
  const topic = elements.find((e) => e.id === topicId);
  const parts = effortParts(eff(topicId), metric, scope);
  const total = parts.events + parts.tasks;
  const children = subTopics(elements, topicId);
  const open = !closed.has(topicId);
  const evPct = rootValue ? (parts.events / rootValue) * 100 : 0;
  const tkPct = rootValue ? (parts.tasks / rootValue) * 100 : 0;

  return (
    <li>
      <div className="flex items-center gap-2" style={{ paddingLeft: depth * 14 }}>
        <button onClick={() => onToggle(topicId)} className={`p-0.5 text-slate-400 ${children.length === 0 ? 'invisible' : ''}`}>
          <ChevronRight size={14} className={`transition-transform ${open ? 'rotate-90' : ''}`} />
        </button>
        <button
          onClick={() => onOpen(topicId)}
          className="text-sm font-medium text-slate-700 dark:text-slate-200 w-40 truncate text-left hover:text-sky-600 dark:hover:text-sky-400 hover:underline"
        >
          {displayName(topic)}
        </button>
        <div
          className="flex-1 max-w-md h-3 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden flex"
          title={`events ${formatMinutes(parts.events)} · tasks ${formatMinutes(parts.tasks)}`}
        >
          <div className="bg-mint-500 h-full" style={{ width: `${evPct}%` }} />
          <div className="bg-lavender-500 h-full" style={{ width: `${tkPct}%` }} />
        </div>
        <span className="w-20 text-right text-sm tabular-nums text-slate-600 dark:text-slate-300">
          {formatMinutes(total)}
        </span>
      </div>
      {open && children.length > 0 && (
        <ul className="space-y-0.5">
          {children.map((c) => (
            <EffortRow
              key={c.id}
              topicId={c.id}
              depth={depth + 1}
              elements={elements}
              eff={eff}
              metric={metric}
              scope={scope}
              rootValue={rootValue}
              closed={closed}
              onToggle={onToggle}
              onOpen={onOpen}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

function Group({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-slate-500">{label}</span>
      <div className="flex gap-1">{children}</div>
    </div>
  );
}

function Toggle({ active, onClick, label, title }: { active: boolean; onClick: () => void; label: string; title?: string }) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={`px-3 py-1.5 rounded-lg border text-sm ${
        active ? 'bg-sky-500 text-white border-sky-500' : 'border-slate-200 dark:border-slate-700'
      }`}
    >
      {label}
    </button>
  );
}
