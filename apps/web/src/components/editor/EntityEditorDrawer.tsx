import { useEffect, useState } from 'react';
import { HelpCircle, Plus, Trash2, X } from 'lucide-react';
import {
  EntityKind,
  EntitySpec,
  createEntity,
  deleteEntity,
  fetchEntity,
  updateEntity,
} from '../../api/client';
import { useData } from '../../data/DataContext';
import { useHelp, KIND_TO_PAGE } from '../../help';

interface Props {
  kind: EntityKind;
  entityId: string | null; // null => create
  onClose: () => void;
  onSaved: () => void;
}

interface KV {
  key: string;
  value: string;
}
interface ScheduleForm {
  type: 'weekly' | 'monthly' | 'yearly' | 'single_day' | 'multi_day';
  weekDays: string[];
  day: string;
  month: string;
  startDay: string;
  endDay: string;
  startTime: string;
  endTime: string;
  duration: string;
  // Optional recurrence bounds (weekly/monthly/yearly), inclusive.
  startDate: string;
  endDate: string;
}

const RECURRING_TYPES = ['weekly', 'monthly', 'yearly'];

const KNOWN_ATTRS = ['status', 'priority', 'deadline', 'location', 'on-focus'];
const WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
const KIND_LABEL: Record<EntityKind, string> = { topics: 'Topic', tasks: 'Task', events: 'Event' };

const asStr = (v: unknown): string => (v === null || v === undefined ? '' : String(v));
const asArr = (v: unknown): string[] =>
  Array.isArray(v) ? v.map(String) : v ? [String(v)] : [];
const isRec = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null && !Array.isArray(v);

function coerce(value: string): unknown {
  const t = value.trim();
  if (t === '') return '';
  if (/^-?\d+$/.test(t)) return parseInt(t, 10);
  if (/^-?\d*\.\d+$/.test(t)) return parseFloat(t);
  if (t === 'true') return true;
  if (t === 'false') return false;
  return value;
}

function emptySchedule(): ScheduleForm {
  return {
    type: 'weekly',
    weekDays: [],
    day: '',
    month: '',
    startDay: '',
    endDay: '',
    startTime: '',
    endTime: '',
    duration: '',
    startDate: '',
    endDate: '',
  };
}

function scheduleFromRaw(raw: Record<string, unknown>): ScheduleForm {
  const s = emptySchedule();
  const type = asStr(raw.type) as ScheduleForm['type'];
  s.type = ['weekly', 'monthly', 'yearly', 'single_day', 'multi_day'].includes(type)
    ? type
    : 'weekly';
  s.weekDays = asArr(raw.week_days);
  s.day = raw.type === 'single_day' ? asStr(raw.day) : asStr(raw.day);
  s.month = asStr(raw.month);
  s.startDay = asStr(raw.start_day);
  s.endDay = asStr(raw.end_day);
  s.startTime = asStr(raw.start_time);
  s.endTime = asStr(raw.end_time);
  s.duration = asStr(raw.duration);
  s.startDate = asStr(raw.start_date);
  s.endDate = asStr(raw.end_date);
  return s;
}

function scheduleToRaw(s: ScheduleForm): EntitySpec {
  const times: EntitySpec = {};
  if (s.startTime) times.start_time = s.startTime;
  if (s.endTime) times.end_time = s.endTime;
  if (s.duration) times.duration = s.duration;
  // Recurrence bounds only apply to repeating schedules.
  const bounds: EntitySpec = {};
  if (RECURRING_TYPES.includes(s.type)) {
    if (s.startDate) bounds.start_date = s.startDate;
    if (s.endDate) bounds.end_date = s.endDate;
  }
  if (s.type === 'weekly') return { type: 'weekly', week_days: s.weekDays, ...times, ...bounds };
  if (s.type === 'monthly')
    return { type: 'monthly', day: Number(s.day) || 1, ...times, ...bounds };
  if (s.type === 'yearly')
    return { type: 'yearly', month: Number(s.month) || 1, day: Number(s.day) || 1, ...times, ...bounds };
  if (s.type === 'single_day') return { type: 'single_day', day: s.day, ...times };
  return { type: 'multi_day', start_day: s.startDay, end_day: s.endDay, ...times };
}

export function EntityEditorDrawer({ kind, entityId, onClose, onSaved }: Props) {
  const { meta } = useData();
  const { openHelp } = useHelp();
  const isEdit = entityId !== null;

  const [id, setId] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [topicIds, setTopicIds] = useState<string[]>([]);
  const [parentId, setParentId] = useState('');
  const [parentIds, setParentIds] = useState<string[]>([]);
  const [tags, setTags] = useState('');
  const [traits, setTraits] = useState<string[]>([]);
  const [color, setColor] = useState('');
  const [shape, setShape] = useState('');
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [deadline, setDeadline] = useState('');
  const [location, setLocation] = useState('');
  const [onFocus, setOnFocus] = useState(false);
  const [attrs, setAttrs] = useState<KV[]>([]);
  const [schedules, setSchedules] = useState<ScheduleForm[]>([]);
  const [relations, setRelations] = useState<{ task: string; type: string }[]>([]);
  const [eventLinks, setEventLinks] = useState<
    { event: string; use_as_deadline: boolean; as_context: boolean }[]
  >([]);

  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isEdit || entityId === null) return;
    fetchEntity(kind, entityId)
      .then((raw) => {
        setId(asStr(raw.id));
        setName(asStr(raw.name));
        setDescription(asStr(raw.description));
        setTopicIds(asArr(raw.topic_ids));
        setParentId(asStr(raw.parent_id));
        setParentIds(asArr(raw.parent_ids));
        setTags(asArr(raw.tags).join(', '));
        setTraits(asArr(raw.traits));
        if (isRec(raw.layout)) {
          const lay = raw.layout;
          if (lay.background) {
            const bg = Array.isArray(lay.background) ? lay.background[0] : lay.background;
            if (isRec(bg)) setColor(asStr(bg.color));
          }
          if (isRec(lay.shape)) setShape(asStr(lay.shape.type));
        }
        const a = isRec(raw.attributes) ? raw.attributes : {};
        setStatus(asStr(a.status));
        setPriority(asStr(a.priority));
        setDeadline(asStr(a.deadline));
        setLocation(asStr(a.location));
        setOnFocus(['true', 'yes', 'on', '1'].includes(asStr(a['on-focus']).toLowerCase()));
        setAttrs(
          Object.entries(a)
            .filter(([k]) => !KNOWN_ATTRS.includes(k))
            .map(([k, v]) => ({ key: k, value: asStr(v) }))
        );
        if (Array.isArray(raw.schedules))
          setSchedules(raw.schedules.filter(isRec).map(scheduleFromRaw));
        if (Array.isArray(raw.relations))
          setRelations(
            raw.relations.filter(isRec).map((r) => ({
              task: asStr(r.task),
              type: asStr(r.type) || 'connected',
            }))
          );
        if (Array.isArray(raw.event_links))
          setEventLinks(
            raw.event_links.filter(isRec).map((l) => ({
              event: asStr(l.event),
              use_as_deadline: Boolean(l.use_as_deadline),
              as_context: Boolean(l.as_context),
            }))
          );
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, [isEdit, entityId, kind]);

  const topicOptions = meta?.topics ?? [];
  const taskOptions = (meta?.tasks ?? []).filter((t) => t.id !== id);
  const eventOptions = meta?.events ?? [];
  const traitOptions = meta?.traits ?? [];

  const buildSpec = (): EntitySpec => {
    const attributes: EntitySpec = {};
    for (const { key, value } of attrs) if (key.trim()) attributes[key.trim()] = coerce(value);
    if (status) attributes.status = status;
    if (priority) attributes.priority = coerce(priority);
    if (deadline) attributes.deadline = deadline;
    if (kind === 'events' && location) attributes.location = location;
    if (kind !== 'topics' && onFocus) attributes['on-focus'] = true;

    const spec: EntitySpec = { id: id.trim(), name: name.trim() };
    if (description.trim()) spec.description = description.trim();
    const tagList = tags.split(',').map((t) => t.trim()).filter(Boolean);
    if (tagList.length) spec.tags = tagList;
    if (traits.length) spec.traits = traits;
    if (Object.keys(attributes).length) spec.attributes = attributes;
    const layout: EntitySpec = {};
    if (color) layout.background = { type: 'solid', color };
    if (shape) layout.shape = { type: shape };
    if (Object.keys(layout).length) spec.layout = layout;

    if (kind === 'topics') {
      if (parentIds.length) spec.parent_ids = parentIds;
    } else {
      if (topicIds.length) spec.topic_ids = topicIds;
      if (parentId) spec.parent_id = parentId;
      if (schedules.length) spec.schedules = schedules.map(scheduleToRaw);
    }
    if (kind === 'tasks') {
      if (relations.length)
        spec.relations = relations.filter((r) => r.task).map((r) => ({ task: r.task, type: r.type }));
      if (eventLinks.length)
        spec.event_links = eventLinks
          .filter((l) => l.event)
          .map((l) => ({
            event: l.event,
            use_as_deadline: l.use_as_deadline,
            as_context: l.as_context,
          }));
    }
    return spec;
  };

  const handleSave = async () => {
    setError(null);
    if (!id.trim()) return setError('An id is required.');
    if (!name.trim()) return setError('A name is required.');
    setSaving(true);
    try {
      const spec = buildSpec();
      if (isEdit && entityId !== null) await updateEntity(kind, entityId, spec);
      else await createEntity(kind, spec);
      onSaved();
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (entityId === null) return;
    if (!window.confirm(`Delete ${KIND_LABEL[kind].toLowerCase()} "${name || entityId}"?`)) return;
    setSaving(true);
    try {
      await deleteEntity(kind, entityId);
      onSaved();
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  const toggle = (list: string[], set: (v: string[]) => void, value: string) =>
    set(list.includes(value) ? list.filter((v) => v !== value) : [...list, value]);

  const field = 'w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-400';
  const label = 'block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wide';
  const chip = (active: boolean) =>
    `px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${
      active
        ? 'bg-sky-500 text-white border-sky-500'
        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700'
    }`;

  const showSchedules = kind !== 'topics';

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative w-full max-w-md h-full bg-white dark:bg-slate-900 shadow-2xl flex flex-col">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">
            {isEdit ? 'Edit' : 'New'} {KIND_LABEL[kind]}
          </h2>
          <div className="flex items-center gap-1">
            <button
              onClick={() => openHelp(KIND_TO_PAGE[kind])}
              title={`Help: ${KIND_LABEL[kind]}`}
              className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <HelpCircle size={18} className="text-slate-500" />
            </button>
            <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
              <X size={18} className="text-slate-500" />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center text-slate-400">Loading…</div>
        ) : (
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
            {kind !== 'topics' && (
              <label
                className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer border ${
                  onFocus
                    ? 'bg-cyan-50 dark:bg-cyan-900/20 border-cyan-300 dark:border-cyan-700'
                    : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700'
                }`}
              >
                <input
                  type="checkbox"
                  className="w-4 h-4 accent-cyan-500"
                  checked={onFocus}
                  onChange={(e) => setOnFocus(e.target.checked)}
                />
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">On focus</span>
                <span className="text-xs text-slate-400">
                  {kind === 'tasks'
                    ? 'show in Focus panel · reveal this sub-task in other panels'
                    : 'show this event in the Focus panel'}
                </span>
              </label>
            )}
            <div>
              <label className={label}>Id</label>
              <input
                className={field}
                value={id}
                disabled={isEdit}
                placeholder="unique-id"
                onChange={(e) => setId(e.target.value)}
              />
            </div>
            <div>
              <label className={label}>Name</label>
              <input className={field} value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div>
              <label className={label}>Description</label>
              <textarea
                className={`${field} h-16 resize-none`}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {kind === 'topics' ? (
              <div>
                <label className={label}>Parent topics</label>
                <div className="flex flex-wrap gap-1.5">
                  {topicOptions
                    .filter((t) => t.id !== id)
                    .map((t) => (
                      <button
                        key={t.id}
                        type="button"
                        className={chip(parentIds.includes(t.id))}
                        onClick={() => toggle(parentIds, setParentIds, t.id)}
                      >
                        {t.name}
                      </button>
                    ))}
                  {topicOptions.length === 0 && <span className="text-xs text-slate-400">none</span>}
                </div>
              </div>
            ) : (
              <div>
                <label className={label}>Topics</label>
                <div className="flex flex-wrap gap-1.5">
                  {topicOptions.map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      className={chip(topicIds.includes(t.id))}
                      onClick={() => toggle(topicIds, setTopicIds, t.id)}
                    >
                      {t.name}
                    </button>
                  ))}
                  {topicOptions.length === 0 && <span className="text-xs text-slate-400">none</span>}
                </div>
              </div>
            )}

            {traitOptions.length > 0 && (
              <div>
                <label className={label}>Traits</label>
                <div className="flex flex-wrap gap-1.5">
                  {traitOptions.map((t) => (
                    <button
                      key={t}
                      type="button"
                      className={chip(traits.includes(t))}
                      onClick={() => toggle(traits, setTraits, t)}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={label}>Tags</label>
                <input
                  className={field}
                  value={tags}
                  placeholder="comma, separated"
                  onChange={(e) => setTags(e.target.value)}
                />
              </div>
              <div>
                <label className={label}>Color (layout)</label>
                <input
                  type="color"
                  className={`${field} h-[38px] p-1`}
                  value={color || '#3b82f6'}
                  onChange={(e) => setColor(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className={label}>Shape (layout)</label>
              <select className={field} value={shape} onChange={(e) => setShape(e.target.value)}>
                <option value="">— inherit —</option>
                <option value="rounded">Rounded</option>
                <option value="rectangle">Rectangle</option>
                <option value="curvy">Curvy</option>
                <option value="cloudy">Cloudy</option>
                <option value="sticky">Sticky</option>
              </select>
            </div>

            {kind === 'tasks' && (
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className={label}>Status</label>
                  <input className={field} list="status-opts" value={status} onChange={(e) => setStatus(e.target.value)} />
                  <datalist id="status-opts">
                    <option value="todo" />
                    <option value="doing" />
                    <option value="done" />
                  </datalist>
                </div>
                <div>
                  <label className={label}>Priority</label>
                  <input className={field} list="prio-opts" value={priority} onChange={(e) => setPriority(e.target.value)} />
                  <datalist id="prio-opts">
                    <option value="low" />
                    <option value="medium" />
                    <option value="high" />
                  </datalist>
                </div>
                <div>
                  <label className={label}>Deadline</label>
                  <input type="date" className={field} value={deadline} onChange={(e) => setDeadline(e.target.value)} />
                </div>
              </div>
            )}


            {kind === 'events' && (
              <div>
                <label className={label}>Location</label>
                <input className={field} value={location} onChange={(e) => setLocation(e.target.value)} />
              </div>
            )}

            {kind !== 'topics' && (
              <div>
                <label className={label}>Parent {kind === 'tasks' ? 'task' : 'event'} (optional)</label>
                <select className={field} value={parentId} onChange={(e) => setParentId(e.target.value)}>
                  <option value="">— none —</option>
                  {(kind === 'tasks' ? taskOptions : eventOptions).map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {showSchedules && (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className={label}>Schedules</label>
                  <button
                    type="button"
                    className="text-xs text-sky-600 dark:text-sky-400 flex items-center gap-1"
                    onClick={() => setSchedules([...schedules, emptySchedule()])}
                  >
                    <Plus size={12} /> add
                  </button>
                </div>
                <div className="space-y-2">
                  {schedules.map((s, i) => (
                    <ScheduleRow
                      key={i}
                      value={s}
                      onChange={(v) => setSchedules(schedules.map((x, j) => (j === i ? v : x)))}
                      onRemove={() => setSchedules(schedules.filter((_, j) => j !== i))}
                    />
                  ))}
                </div>
              </div>
            )}

            {kind === 'tasks' && (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className={label}>Relations</label>
                  <button
                    type="button"
                    className="text-xs text-sky-600 dark:text-sky-400 flex items-center gap-1"
                    onClick={() => setRelations([...relations, { task: '', type: 'requires' }])}
                  >
                    <Plus size={12} /> add
                  </button>
                </div>
                <div className="space-y-2">
                  {relations.map((r, i) => (
                    <div key={i} className="flex gap-1.5 items-center">
                      <select
                        className={`${field} flex-1`}
                        value={r.type}
                        onChange={(e) =>
                          setRelations(relations.map((x, j) => (j === i ? { ...x, type: e.target.value } : x)))
                        }
                      >
                        {['requires', 'needs', 'connected', 'similar'].map((t) => (
                          <option key={t} value={t}>
                            {t}
                          </option>
                        ))}
                      </select>
                      <select
                        className={`${field} flex-1`}
                        value={r.task}
                        onChange={(e) =>
                          setRelations(relations.map((x, j) => (j === i ? { ...x, task: e.target.value } : x)))
                        }
                      >
                        <option value="">— task —</option>
                        {taskOptions.map((o) => (
                          <option key={o.id} value={o.id}>
                            {o.name}
                          </option>
                        ))}
                      </select>
                      <button type="button" onClick={() => setRelations(relations.filter((_, j) => j !== i))}>
                        <Trash2 size={14} className="text-slate-400 hover:text-coral-500" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className={label}>Other attributes</label>
                <button
                  type="button"
                  className="text-xs text-sky-600 dark:text-sky-400 flex items-center gap-1"
                  onClick={() => setAttrs([...attrs, { key: '', value: '' }])}
                >
                  <Plus size={12} /> add
                </button>
              </div>
              <div className="space-y-2">
                {attrs.map((kv, i) => (
                  <div key={i} className="flex gap-1.5 items-center">
                    <input
                      className={`${field} flex-1`}
                      placeholder="key"
                      value={kv.key}
                      onChange={(e) => setAttrs(attrs.map((x, j) => (j === i ? { ...x, key: e.target.value } : x)))}
                    />
                    <input
                      className={`${field} flex-1`}
                      placeholder="value"
                      value={kv.value}
                      onChange={(e) => setAttrs(attrs.map((x, j) => (j === i ? { ...x, value: e.target.value } : x)))}
                    />
                    <button type="button" onClick={() => setAttrs(attrs.filter((_, j) => j !== i))}>
                      <Trash2 size={14} className="text-slate-400 hover:text-coral-500" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {error && (
              <p className="text-sm text-coral-600 dark:text-coral-400 bg-coral-50 dark:bg-coral-900/20 rounded-lg px-3 py-2">
                {error}
              </p>
            )}
          </div>
        )}

        <div className="flex items-center justify-between gap-2 px-5 py-4 border-t border-slate-200 dark:border-slate-800">
          {isEdit ? (
            <button
              onClick={handleDelete}
              disabled={saving}
              className="px-3 py-2 rounded-lg text-sm font-medium text-coral-600 hover:bg-coral-50 dark:hover:bg-coral-900/20 flex items-center gap-1.5"
            >
              <Trash2 size={15} /> Delete
            </button>
          ) : (
            <span />
          )}
          <div className="flex gap-2">
            <button onClick={onClose} className="px-4 py-2 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800">
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-4 py-2 rounded-lg text-sm font-semibold bg-sky-500 text-white hover:bg-sky-600 disabled:opacity-50"
            >
              {saving ? 'Saving…' : 'Save'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ScheduleRow({
  value,
  onChange,
  onRemove,
}: {
  value: ScheduleForm;
  onChange: (v: ScheduleForm) => void;
  onRemove: () => void;
}) {
  const f = 'px-2 py-1 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-slate-800 dark:text-slate-100';
  const set = (patch: Partial<ScheduleForm>) => onChange({ ...value, ...patch });
  const toggleDay = (d: string) =>
    set({ weekDays: value.weekDays.includes(d) ? value.weekDays.filter((x) => x !== d) : [...value.weekDays, d] });

  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-700 p-2 space-y-2">
      <div className="flex gap-1.5 items-center">
        <select className={`${f} flex-1`} value={value.type} onChange={(e) => set({ type: e.target.value as ScheduleForm['type'] })}>
          <option value="weekly">weekly</option>
          <option value="monthly">monthly</option>
          <option value="yearly">yearly</option>
          <option value="single_day">single day</option>
          <option value="multi_day">multi day</option>
        </select>
        <button type="button" onClick={onRemove}>
          <Trash2 size={14} className="text-slate-400 hover:text-coral-500" />
        </button>
      </div>

      {value.type === 'weekly' && (
        <div className="flex flex-wrap gap-1">
          {WEEKDAYS.map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => toggleDay(d)}
              className={`px-1.5 py-0.5 rounded text-[10px] uppercase ${
                value.weekDays.includes(d) ? 'bg-sky-500 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-500'
              }`}
            >
              {d.slice(0, 3)}
            </button>
          ))}
        </div>
      )}
      {value.type === 'monthly' && (
        <input className={f} type="number" min={1} max={31} placeholder="day of month" value={value.day} onChange={(e) => set({ day: e.target.value })} />
      )}
      {value.type === 'yearly' && (
        <div className="flex gap-1.5">
          <input className={f} type="number" min={1} max={12} placeholder="month" value={value.month} onChange={(e) => set({ month: e.target.value })} />
          <input className={f} type="number" min={1} max={31} placeholder="day" value={value.day} onChange={(e) => set({ day: e.target.value })} />
        </div>
      )}
      {value.type === 'single_day' && (
        <input className={f} type="date" value={value.day} onChange={(e) => set({ day: e.target.value })} />
      )}
      {value.type === 'multi_day' && (
        <div className="flex gap-1.5">
          <input className={f} type="date" value={value.startDay} onChange={(e) => set({ startDay: e.target.value })} />
          <input className={f} type="date" value={value.endDay} onChange={(e) => set({ endDay: e.target.value })} />
        </div>
      )}
      <div className="flex gap-1.5">
        <input className={f} type="time" value={value.startTime} onChange={(e) => set({ startTime: e.target.value })} />
        <input className={f} placeholder="dur e.g. 1h" value={value.duration} onChange={(e) => set({ duration: e.target.value })} />
      </div>

      {RECURRING_TYPES.includes(value.type) && (
        <div className="flex gap-1.5 items-center">
          <span className="text-[10px] text-slate-400 uppercase">runs</span>
          <input
            className={f}
            type="date"
            title="Repeats from (optional)"
            value={value.startDate}
            onChange={(e) => set({ startDate: e.target.value })}
          />
          <span className="text-[10px] text-slate-400">→</span>
          <input
            className={f}
            type="date"
            title="Repeats until (optional)"
            value={value.endDate}
            onChange={(e) => set({ endDate: e.target.value })}
          />
        </div>
      )}
    </div>
  );
}
