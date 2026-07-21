import { useMemo, useState, ReactNode } from 'react';
import { Search, ChevronLeft, ChevronRight, ChevronDown, FolderOpen, ListTodo, CalendarPlus, Boxes } from 'lucide-react';
import { EntityKind } from '../api/client';
import { useData } from '../data/DataContext';
import { useElement } from '../data/ElementContext';
import { orderTopics } from '../lib/topics';
import { useCollapse } from '../lib/useCollapse';
import { ElementDetail } from '../components/element/ElementDetail';

interface Entry {
  kind: EntityKind;
  id: string;
  name: string;
  depth: number;
}

const GROUPS: { kind: EntityKind; label: string; icon: ReactNode }[] = [
  { kind: 'topics', label: 'Topics', icon: <FolderOpen size={14} /> },
  { kind: 'tasks', label: 'Tasks', icon: <ListTodo size={14} /> },
  { kind: 'events', label: 'Events', icon: <CalendarPlus size={14} /> },
];

/** A collapsible kind-group in the element finder. */
function FinderGroup({
  kind,
  label,
  icon,
  items,
  renderItem,
}: {
  kind: EntityKind;
  label: string;
  icon: ReactNode;
  items: Entry[];
  renderItem: (e: Entry) => ReactNode;
}) {
  const { collapsed, toggle } = useCollapse(`element-finder-${kind}`);
  return (
    <div>
      <button
        onClick={toggle}
        className="w-full flex items-center gap-1.5 px-2 py-1 text-xs font-semibold uppercase tracking-wide text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
      >
        <ChevronDown size={13} className={`transition-transform ${collapsed ? '-rotate-90' : ''}`} />
        {icon} {label} <span className="font-normal">({items.length})</span>
      </button>
      {!collapsed && <div className="space-y-0.5 mt-0.5">{items.map(renderItem)}</div>}
    </div>
  );
}

export function ElementPage() {
  const { meta, topics } = useData();
  const { selected, openElement } = useElement();
  const [query, setQuery] = useState('');

  // Flat, searchable index of every entity. Topics keep their hierarchy depth.
  const all: Entry[] = useMemo(() => {
    if (!meta) return [];
    return [
      ...orderTopics(topics).map(({ topic, depth }) => ({
        kind: 'topics' as const, id: topic.id, name: topic.name, depth,
      })),
      ...meta.tasks.map((t) => ({ kind: 'tasks' as const, id: t.id, name: t.name, depth: 0 })),
      ...meta.events.map((e) => ({ kind: 'events' as const, id: e.id, name: e.name, depth: 0 })),
    ];
  }, [meta, topics]);

  const q = query.trim().toLowerCase();
  const filtered = q
    ? all.filter((e) => e.name.toLowerCase().includes(q) || e.id.toLowerCase().includes(q))
    : all;

  // prev/next move through the filtered list (falls back to the full list).
  const nav = filtered.length ? filtered : all;
  const idx = selected ? nav.findIndex((e) => e.kind === selected.kind && e.id === selected.id) : -1;
  const go = (delta: number) => {
    if (!nav.length) return;
    const next = idx < 0 ? 0 : (idx + delta + nav.length) % nav.length;
    openElement(nav[next].kind, nav[next].id);
  };

  const itemBtn = (e: Entry) => {
    const active = selected?.kind === e.kind && selected?.id === e.id;
    return (
      <button
        key={`${e.kind}:${e.id}`}
        onClick={() => openElement(e.kind, e.id)}
        className={`w-full text-left px-3 py-1.5 rounded-lg text-sm truncate transition-colors ${
          active
            ? 'bg-sky-500 text-white'
            : 'text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800'
        }`}
        style={{ paddingLeft: 12 + e.depth * 14 }}
        title={e.name}
      >
        {e.depth > 0 && <span className="text-slate-300 dark:text-slate-600">└ </span>}
        {e.name}
      </button>
    );
  };

  return (
    <div className="grid gap-4 md:grid-cols-[280px_1fr] items-start">
      {/* finder */}
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col" style={{ maxHeight: 'calc(100vh - 9rem)' }}>
        <div className="p-3 border-b border-slate-200 dark:border-slate-800">
          <div className="relative">
            <Search size={15} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Find an element…"
              className="w-full pl-8 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-400"
            />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-3">
          {GROUPS.map((g) => {
            const items = filtered.filter((e) => e.kind === g.kind);
            if (!items.length) return null;
            return (
              <FinderGroup key={g.kind} kind={g.kind} label={g.label} icon={g.icon} items={items} renderItem={itemBtn} />
            );
          })}
          {filtered.length === 0 && (
            <p className="text-sm text-slate-400 text-center py-6">No matches.</p>
          )}
        </div>
      </div>

      {/* detail */}
      <div className="space-y-3 min-w-0">
        {selected ? (
          <>
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm text-slate-400">
                {idx >= 0 ? `${idx + 1} of ${nav.length}` : ''}
              </span>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => go(-1)}
                  className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-700 dark:hover:text-slate-200"
                  title="Previous element"
                >
                  <ChevronLeft size={16} />
                </button>
                <button
                  onClick={() => go(1)}
                  className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-700 dark:hover:text-slate-200"
                  title="Next element"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
            <ElementDetail
              key={`${selected.kind}:${selected.id}`}
              kind={selected.kind}
              entityId={selected.id}
              onNavigate={openElement}
            />
          </>
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 py-20 text-center text-slate-400">
            <Boxes size={40} className="mx-auto mb-3 opacity-50" />
            <p className="font-medium">Pick an element to inspect</p>
            <p className="text-sm">Search on the left, or double-click any item in another panel.</p>
          </div>
        )}
      </div>
    </div>
  );
}
