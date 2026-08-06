import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { ChevronRight, ChevronsDownUp, ChevronsUpDown, Plus, Save, Trash2 } from 'lucide-react';
import { useData } from '../store';
import { useSettings } from '../settings';
import { fetchElement } from '../api';
import { AttributeDefinitionDTO, ElementDTO, ElementSpec, ElementType, LayoutDTO } from '../types';
import {
  attrBool,
  attrString,
  byType,
  childrenOf,
  displayName,
  isCancelled,
  rootTopics,
  subTopics,
  whenOf,
} from '../lib/elements';
import { fmtDate } from '../lib/format';

const TYPE_LABEL: Record<ElementType, string> = {
  topic: 'Topics',
  event: 'Events',
  task: 'Tasks',
  schedule: 'Schedules',
};

const CONFIG_TITLE: Record<ElementType, string> = {
  topic: 'Topic Configuration',
  event: 'Event Configuration',
  task: 'Task Configuration',
  schedule: 'Schedule Configuration',
};

interface Props {
  type: ElementType;
  /** When set, preselect this element (used by the "Configure" jump / history). */
  pendingId?: string;
}

export function ElementManagement({ type, pendingId }: Props) {
  const { elements, byId, definitions, save, remove } = useData();
  const { settings } = useSettings();
  const autoSave = settings.autoSave;

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draft, setDraft] = useState<ElementSpec | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [closed, setClosed] = useState<Set<string>>(new Set());

  const selected = selectedId ? byId[selectedId] : undefined;

  // Refs so the auto-save flush always sees the latest values.
  const dirtyRef = useRef(false);
  const draftRef = useRef<ElementSpec | null>(null);
  const selectedIdRef = useRef<string | null>(null);
  draftRef.current = draft;
  selectedIdRef.current = selectedId;

  const flush = useCallback(async () => {
    if (!dirtyRef.current) return;
    const d = draftRef.current;
    if (!d || !selectedIdRef.current) return; // never auto-create brand-new elements
    dirtyRef.current = false;
    try {
      await save(d);
    } catch {
      /* errors surface on manual save */
    }
  }, [save]);

  // Flush once more when leaving the panel entirely.
  const flushRef = useRef(flush);
  flushRef.current = flush;
  useEffect(() => () => void flushRef.current(), []);

  // Load the raw (own) values of the selected element into the draft. Keyed on
  // selectedId only, so a background reload never clobbers in-progress edits.
  useEffect(() => {
    dirtyRef.current = false;
    if (!selectedId) {
      setDraft((d) => (d && !selectedIdRef.current ? d : null)); // keep a new-element draft
      return;
    }
    const el = byId[selectedId];
    if (el?.virtual) {
      setDraft({
        id: el.id,
        type: el.type,
        directParents: el.mainParent ? [el.mainParent] : [],
        attributes: {},
        layout: {},
      });
      return;
    }
    fetchElement(selectedId)
      .then((raw) =>
        setDraft({
          id: raw.id,
          type: raw.type,
          directParents: raw.directParents ?? [],
          attributes: raw.attributes ?? {},
          layout: raw.layout ?? {},
        }),
      )
      .catch(() => setDraft(null));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedId]);

  // Preselect the element requested by navigation (Configure / history).
  useEffect(() => {
    if (pendingId) setSelectedId(pendingId);
  }, [pendingId]);

  // Debounced auto-save while editing an existing element.
  useEffect(() => {
    if (!autoSave || !selectedId || !dirtyRef.current) return;
    const t = setTimeout(() => void flush(), 700);
    return () => clearTimeout(t);
  }, [draft, autoSave, selectedId, flush]);

  const relevantDefs = useMemo(
    () =>
      definitions.filter(
        (d) =>
          (d.appliesTo.length === 0 || d.appliesTo.includes(type)) &&
          !['name', 'description', 'connections'].includes(d.name),
      ),
    [definitions, type],
  );

  const allTopicIds = useMemo(() => byType(elements, 'topic').map((t) => t.id), [elements]);

  const selectElement = useCallback(
    (id: string) => {
      void flush(); // save the outgoing element before switching
      setSelectedId(id);
      setMessage(null);
    },
    [flush],
  );

  const startNew = () => {
    void flush();
    const base = `${type}-${Date.now().toString(36)}`;
    dirtyRef.current = false;
    setSelectedId(null);
    setDraft({ id: base, type, directParents: [], attributes: { name: `New ${type}` }, layout: {} });
  };

  const mutate = (updater: (d: ElementSpec) => ElementSpec) => {
    dirtyRef.current = true;
    setDraft((d) => (d ? updater(d) : d));
  };

  const setAttr = (key: string, value: unknown) =>
    mutate((d) => ({ ...d, attributes: { ...(d.attributes ?? {}), [key]: value } }));

  const clearAttr = (key: string) =>
    mutate((d) => {
      const next = { ...(d.attributes ?? {}) };
      delete next[key];
      return { ...d, attributes: next };
    });

  const setLayout = (patch: Partial<LayoutDTO>) =>
    mutate((d) => ({ ...d, layout: { ...(d.layout ?? {}), ...patch } }));

  const onSave = async () => {
    if (!draft || !draft.id) return;
    setBusy(true);
    setMessage(null);
    try {
      await save(draft);
      dirtyRef.current = false;
      setSelectedId(draft.id);
      setMessage('Saved.');
    } catch (e) {
      setMessage(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const onDelete = async () => {
    if (!draft?.id) return;
    setBusy(true);
    try {
      dirtyRef.current = false;
      await remove(draft.id);
      setSelectedId(null);
      setDraft(null);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-4">
      {/* Left: topic tree with elements of this type */}
      <div className="card p-3 h-fit">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-slate-700 dark:text-slate-200">{TYPE_LABEL[type]}</h3>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setClosed(new Set(allTopicIds))}
              title="Collapse all"
              className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <ChevronsDownUp size={15} />
            </button>
            <button
              onClick={() => setClosed(new Set())}
              title="Expand all"
              className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <ChevronsUpDown size={15} />
            </button>
            <button
              onClick={startNew}
              className="p-1.5 rounded-lg bg-sky-500 text-white hover:bg-sky-600"
              title="New element"
            >
              <Plus size={16} />
            </button>
          </div>
        </div>
        <ElementTree
          type={type}
          selectedId={selectedId}
          onSelect={selectElement}
          closed={closed}
          onToggle={(id) =>
            setClosed((prev) => {
              const next = new Set(prev);
              if (next.has(id)) next.delete(id);
              else next.add(id);
              return next;
            })
          }
        />
      </div>

      {/* Center: configuration editor */}
      <div className="card p-4">
        <div className="flex items-center justify-between gap-2 mb-4">
          <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">{CONFIG_TITLE[type]}</h2>
          {autoSave ? (
            <span className="text-xs text-slate-400">auto-save on</span>
          ) : (
            <span className="text-xs text-slate-400">manual save</span>
          )}
        </div>

        {!draft ? (
          <p className="text-slate-400 text-sm">Select an element to configure, or create a new one.</p>
        ) : (
          <div className="space-y-5">
            <div className="flex items-center justify-between gap-2">
              {selectedId ? (
                <span className="font-mono text-sm text-slate-500 truncate">{draft.id}</span>
              ) : (
                <input
                  value={draft.id}
                  onChange={(e) => setDraft({ ...draft, id: e.target.value })}
                  className="font-mono text-sm px-2 py-1 rounded border border-slate-200 dark:border-slate-700 bg-transparent"
                  placeholder="element-id"
                />
              )}
              <div className="flex items-center gap-2">
                {selected?.virtual && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
                    editing promotes this auto-element
                  </span>
                )}
                <button
                  onClick={onSave}
                  disabled={busy}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-sky-500 text-white text-sm hover:bg-sky-600 disabled:opacity-50"
                >
                  <Save size={15} /> Save
                </button>
                {selected && !selected.virtual && (
                  <button
                    onClick={onDelete}
                    disabled={busy}
                    className="p-1.5 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/30"
                    title="Delete"
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            </div>

            {message && <p className="text-sm text-slate-500">{message}</p>}

            <Field label="Name">
              <input
                value={String((draft.attributes ?? {})['name'] ?? '')}
                onChange={(e) => setAttr('name', e.target.value)}
                className="input"
              />
            </Field>
            <Field label="Description">
              <textarea
                value={String((draft.attributes ?? {})['description'] ?? '')}
                onChange={(e) => setAttr('description', e.target.value)}
                className="input min-h-[70px]"
              />
            </Field>
            <Field label="Direct parents (inheritance, first = MainParent)">
              <input
                value={(draft.directParents ?? []).join(', ')}
                onChange={(e) =>
                  mutate((d) => ({
                    ...d,
                    directParents: e.target.value
                      .split(',')
                      .map((s) => s.trim())
                      .filter(Boolean),
                  }))
                }
                className="input font-mono text-sm"
                placeholder="AllTopic"
              />
            </Field>

            <div>
              <h4 className="font-semibold text-slate-600 dark:text-slate-300 mb-2 text-sm uppercase tracking-wide">
                Attributes
              </h4>
              <div className="space-y-2">
                {relevantDefs.map((def) => (
                  <AttributeField
                    key={def.name}
                    def={def}
                    value={(draft.attributes ?? {})[def.name]}
                    onChange={(v) => (v === undefined ? clearAttr(def.name) : setAttr(def.name, v))}
                  />
                ))}
              </div>
            </div>

            <LayoutEditor layout={draft.layout ?? {}} onChange={setLayout} />

            {selected && <RelatedSection element={selected} elements={elements} onOpen={selectElement} />}

            {selected && (selected.connections.length > 0 || selected.incoming.length > 0) && (
              <div>
                <h4 className="font-semibold text-slate-600 dark:text-slate-300 mb-2 text-sm uppercase tracking-wide">
                  Connections
                </h4>
                <ul className="text-sm space-y-1">
                  {selected.connections.map((c, i) => (
                    <li key={`o${i}`} className="text-slate-600 dark:text-slate-300">
                      → <span className="font-medium">{c.relation}</span> {displayName(byId[c.to])}
                    </li>
                  ))}
                  {selected.incoming.map((c, i) => (
                    <li key={`i${i}`} className="text-slate-500">
                      ← {displayName(byId[c.from])} <span className="font-medium">{c.relation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-sm text-slate-500 dark:text-slate-400 mb-1">{label}</span>
      {children}
    </label>
  );
}

function AttributeField({
  def,
  value,
  onChange,
}: {
  def: AttributeDefinitionDTO;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  if (def.valueType === 'bool') {
    return (
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={value === true} onChange={(e) => onChange(e.target.checked)} />
        <span>{def.name}</span>
      </label>
    );
  }
  if (def.valueType === 'enum') {
    return (
      <label className="flex items-center gap-2 text-sm">
        <span className="w-32 text-slate-500">{def.name}</span>
        <select
          value={String(value ?? '')}
          onChange={(e) => onChange(e.target.value || undefined)}
          className="input"
        >
          <option value="">—</option>
          {(def.enumValues ?? []).map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </label>
    );
  }
  const inputType =
    def.valueType === 'int' || def.valueType === 'number'
      ? 'number'
      : def.valueType === 'date'
        ? 'date'
        : 'text';
  return (
    <label className="flex items-center gap-2 text-sm">
      <span className="w-32 text-slate-500">{def.name}</span>
      <input
        type={inputType}
        value={value === undefined || value === null ? '' : String(value)}
        min={def.min}
        max={def.max}
        onChange={(e) => {
          const raw = e.target.value;
          if (raw === '') return onChange(undefined);
          if (inputType === 'number') return onChange(Number(raw));
          onChange(raw);
        }}
        className="input"
        placeholder={def.valueType}
      />
    </label>
  );
}

function LayoutEditor({
  layout,
  onChange,
}: {
  layout: LayoutDTO;
  onChange: (patch: Partial<LayoutDTO>) => void;
}) {
  return (
    <div>
      <h4 className="font-semibold text-slate-600 dark:text-slate-300 mb-2 text-sm uppercase tracking-wide">
        Layout
      </h4>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <label className="flex items-center gap-2">
          <span className="w-24 text-slate-500">Background</span>
          <input
            type="color"
            value={layout.background?.color ?? '#ffffff'}
            onChange={(e) => onChange({ background: { ...layout.background, color: e.target.value } })}
          />
        </label>
        <label className="flex items-center gap-2">
          <span className="w-24 text-slate-500">Border</span>
          <input
            type="color"
            value={layout.border?.color ?? '#94a3b8'}
            onChange={(e) =>
              onChange({
                border: {
                  color: e.target.value,
                  width: layout.border?.width ?? '1px',
                  style: layout.border?.style ?? 'solid',
                },
              })
            }
          />
        </label>
        <label className="flex items-center gap-2">
          <span className="w-24 text-slate-500">Shape</span>
          <select
            value={layout.shape ?? ''}
            onChange={(e) => onChange({ shape: e.target.value || undefined })}
            className="input"
          >
            <option value="">—</option>
            <option value="rectangle">rectangle</option>
            <option value="rounded_rectangle">rounded</option>
            <option value="ellipse">ellipse</option>
            <option value="diamond">diamond</option>
          </select>
        </label>
        <label className="flex items-center gap-2">
          <span className="w-24 text-slate-500">Icon</span>
          <input
            value={layout.icon?.value ?? ''}
            onChange={(e) =>
              onChange({ icon: e.target.value ? { type: 'emoji', value: e.target.value } : undefined })
            }
            className="input"
            placeholder="📐"
          />
        </label>
      </div>
    </div>
  );
}

// --- Per-type related / preview section ------------------------------------

function RelatedSection({
  element,
  elements,
  onOpen,
}: {
  element: ElementDTO;
  elements: ElementDTO[];
  onOpen: (id: string) => void;
}) {
  const children = childrenOf(elements, element.id);

  if (element.type === 'topic') {
    const inTopic = elements.filter((e) => e.topic === element.id);
    return (
      <Section title="Members">
        <div className="flex flex-wrap gap-2 text-sm">
          <StatChip n={subTopics(elements, element.id).length} label="sub-topics" />
          <StatChip n={inTopic.filter((e) => e.type === 'task').length} label="tasks" />
          <StatChip n={inTopic.filter((e) => e.type === 'event').length} label="events" />
          <StatChip n={inTopic.filter((e) => e.type === 'schedule').length} label="schedules" />
        </div>
      </Section>
    );
  }

  if (element.type === 'task') {
    const subs = children.filter((c) => c.type === 'task');
    if (subs.length === 0) return null;
    const marked = subs.filter((s) => attrBool(s, 'marked'));
    const done = marked.filter((s) => attrString(s, 'status') === 'completed').length;
    const pct = marked.length ? Math.round((done / marked.length) * 100) : 0;
    return (
      <Section title={`Subtasks — ${pct}% of marked complete`}>
        <ul className="space-y-1 text-sm">
          {subs.map((s) => (
            <li key={s.id} className="flex items-center gap-2">
              <span className={attrBool(s, 'marked') ? 'text-sky-500' : 'text-slate-300'}>●</span>
              <button
                onClick={() => onOpen(s.id)}
                className={`hover:underline ${
                  attrString(s, 'status') === 'completed' ? 'line-through text-slate-400' : ''
                }`}
              >
                {displayName(s)}
              </button>
              <span className="text-xs text-slate-400">{attrString(s, 'status') ?? ''}</span>
            </li>
          ))}
        </ul>
      </Section>
    );
  }

  // schedule or event: show the occurrences/reminders it generates
  const occ = children
    .filter((c) => !isCancelled(c))
    .sort((a, b) => (whenOf(a)?.getTime() ?? 0) - (whenOf(b)?.getTime() ?? 0))
    .slice(0, 8);
  if (occ.length === 0) return null;
  const label = element.type === 'schedule' ? 'Generated occurrences (preview)' : 'Generated events';
  return (
    <Section title={label}>
      <ul className="space-y-1 text-sm text-slate-600 dark:text-slate-300">
        {occ.map((o) => {
          const w = whenOf(o);
          const cls = attrString(o, 'class');
          return (
            <li key={o.id} className="flex items-center gap-2">
              <span className="text-slate-400">{w ? fmtDate(w) : o.id}</span>
              {cls && cls !== 'normal' && <span className="text-xs uppercase text-slate-400">{cls}</span>}
            </li>
          );
        })}
      </ul>
    </Section>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="font-semibold text-slate-600 dark:text-slate-300 mb-2 text-sm uppercase tracking-wide">
        {title}
      </h4>
      {children}
    </div>
  );
}

function StatChip({ n, label }: { n: number; label: string }) {
  return (
    <span className="px-2 py-1 rounded-lg bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-300">
      <b>{n}</b> {label}
    </span>
  );
}

// --- Topic tree of elements ------------------------------------------------

interface TreeProps {
  type: ElementType;
  selectedId: string | null;
  onSelect: (id: string) => void;
  closed: Set<string>;
  onToggle: (id: string) => void;
}

function ElementTree({ type, selectedId, onSelect, closed, onToggle }: TreeProps) {
  const { elements } = useData();
  const roots = rootTopics(elements);
  return (
    <ul className="space-y-0.5">
      {roots.map((t) => (
        <TopicNode
          key={t.id}
          topicId={t.id}
          depth={0}
          selectedId={selectedId}
          onSelect={onSelect}
          closed={closed}
          onToggle={onToggle}
          leafType={type === 'topic' ? undefined : type}
          selectableTopics={type === 'topic'}
        />
      ))}
    </ul>
  );
}

function TopicNode({
  topicId,
  depth,
  selectedId,
  onSelect,
  closed,
  onToggle,
  leafType,
  selectableTopics,
}: {
  topicId: string;
  depth: number;
  selectedId: string | null;
  onSelect: (id: string) => void;
  closed: Set<string>;
  onToggle: (id: string) => void;
  leafType?: ElementType;
  selectableTopics?: boolean;
}) {
  const { elements, byId } = useData();
  const open = !closed.has(topicId);
  const topic = byId[topicId];
  const children = subTopics(elements, topicId);
  const leaves = leafType
    ? byType(elements, leafType).filter((e) => e.topic === topicId && !e.virtual)
    : [];

  return (
    <li>
      <div className="flex items-center gap-1" style={{ paddingLeft: depth * 12 }}>
        <button onClick={() => onToggle(topicId)} className="text-slate-400 p-0.5">
          <ChevronRight size={14} className={`transition-transform ${open ? 'rotate-90' : ''}`} />
        </button>
        <button
          onClick={() => selectableTopics && onSelect(topicId)}
          className={`text-sm truncate flex-1 text-left px-1 rounded ${
            selectedId === topicId ? 'bg-sky-100 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300' : ''
          }`}
        >
          {displayName(topic)}
        </button>
      </div>
      {open && (
        <ul className="space-y-0.5">
          {children.map((c) => (
            <TopicNode
              key={c.id}
              topicId={c.id}
              depth={depth + 1}
              selectedId={selectedId}
              onSelect={onSelect}
              closed={closed}
              onToggle={onToggle}
              leafType={leafType}
              selectableTopics={selectableTopics}
            />
          ))}
          {leaves.map((leaf) => (
            <li key={leaf.id} style={{ paddingLeft: (depth + 1) * 12 + 18 }}>
              <button
                onClick={() => onSelect(leaf.id)}
                className={`text-sm truncate w-full text-left px-1 py-0.5 rounded ${
                  selectedId === leaf.id
                    ? 'bg-sky-100 dark:bg-sky-900/40 text-sky-700 dark:text-sky-300'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                {attrString(leaf, 'name') ?? leaf.id}
              </button>
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}
