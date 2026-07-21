import { useState } from 'react';
import { ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { DisplayItem, GlobalControls } from '../components/ui';
import { useData } from '../data/DataContext';
import { useEditor } from '../data/EditorContext';
import { useElement } from '../data/ElementContext';
import { usePanelConfig } from '../data/usePanelConfig';
import { itemListClass } from '../lib/itemList';
import { orderTasks } from '../lib/tasks';
import { orderTopics } from '../lib/topics';
import { baseId } from '../api/client';
import { Density } from '../types';

const SHORT_DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export function Agenda() {
  const { tasks: mockTasks, events: mockEvents, topics: mockTopics } = useData();
  const { openEdit, openCreate, canEdit } = useEditor();
  const { openElement } = useElement();
  const { view, setView } = usePanelConfig('agenda');
  const density = 'comfortable' as Density;

  // Topic hierarchy + show/hide filter for the legend.
  const topicById = new Map(mockTopics.map((t) => [t.id, t]));
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
    return out;
  };
  const hasChildren = (id: string) => mockTopics.some((t) => parentOf(t.id) === id);
  const [hiddenTopics, setHiddenTopics] = useState<Set<string>>(new Set());
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set());
  const topicVisible = (topicId?: string) =>
    !topicId || chainOf(topicId).every((id) => !hiddenTopics.has(id));
  const flip = (s: Set<string>, id: string) => {
    const n = new Set(s);
    if (n.has(id)) n.delete(id);
    else n.add(id);
    return n;
  };
  const toggleHidden = (id: string) => setHiddenTopics((s) => flip(s, id));
  const toggleExpanded = (id: string) => setExpandedTopics((s) => flip(s, id));

  const [currentWeekStart, setCurrentWeekStart] = useState(() => {
    const today = new Date();
    const dayOfWeek = today.getDay();
    const diff = today.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    return new Date(today.setDate(diff));
  });

  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const day = new Date(currentWeekStart);
    day.setDate(day.getDate() + i);
    return day;
  });

  const shiftWeek = (delta: number) => {
    const d = new Date(currentWeekStart);
    d.setDate(d.getDate() + delta * 7);
    setCurrentWeekStart(d);
  };
  const goToToday = () => {
    const today = new Date();
    const dow = today.getDay();
    const diff = today.getDate() - dow + (dow === 0 ? -6 : 1);
    setCurrentWeekStart(new Date(today.setDate(diff)));
  };

  const getItemsForDay = (date: Date) => {
    const events = mockEvents.filter(
      (e) => new Date(e.date).toDateString() === date.toDateString() && topicVisible(e.topicId)
    );
    const tasks = mockTasks.filter((t) => {
      const checkDate = t.startDate || t.deadline;
      return (
        checkDate &&
        new Date(checkDate).toDateString() === date.toDateString() &&
        topicVisible(t.topicId)
      );
    });
    return { events, tasks: tasks.filter((t) => t.status !== 'done') };
  };

  const isToday = (date: Date) => date.toDateString() === new Date().toDateString();

  const pad = density === 'expanded' ? 'p-3' : density === 'comfortable' ? 'p-2.5' : 'p-1.5';

  const renderDay = (date: Date, index: number, compact = false) => {
    const { events, tasks } = getItemsForDay(date);
    const today = isToday(date);
    const empty = events.length + tasks.length === 0;

    return (
      <div className="flex flex-col min-h-0 h-full">
        <div className={`flex items-baseline justify-between ${pad} pb-1 shrink-0`}>
          <span className={`text-xs font-semibold ${today ? 'text-sky-600 dark:text-sky-400' : 'text-slate-500 dark:text-slate-400'}`}>
            {SHORT_DAYS[index]}
          </span>
          <span
            className={
              today
                ? 'inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold bg-gradient-to-br from-sky-400 to-lavender-500 text-white'
                : `${compact ? 'text-sm' : 'text-base'} font-bold text-slate-700 dark:text-slate-200`
            }
          >
            {date.getDate()}
          </span>
        </div>
        <div className={`flex-1 min-h-0 overflow-y-auto ${pad} pt-0 ${itemListClass(view)}`}>
          {events.map((event) => (
            <DisplayItem
              key={event.id}
              title={event.title}
              displayStyle={view}
              itemStyle={event.style}
              topicId={event.topicId}
              startTime={event.startTime}
              endTime={event.endTime}
              recurring={event.recurring}
              onClick={() => openEdit('events', baseId(event.id))}
              onDoubleClick={() => openElement('events', baseId(event.id))}
            />
          ))}
          {orderTasks(tasks).map(({ task, depth }) => (
            <DisplayItem
              key={task.id}
              title={task.title}
              description={task.description}
              displayStyle={view}
              itemStyle={task.style}
              topicId={task.topicId}
              priority={task.priority}
              deadline={task.deadline}
              depth={depth}
              onClick={() => openEdit('tasks', baseId(task.id))}
              onDoubleClick={() => openElement('tasks', baseId(task.id))}
            />
          ))}
          {empty && canEdit && (
            <button
              onClick={() => openCreate('events')}
              className="w-full flex items-center justify-center gap-1 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 py-2 rounded-lg hover:bg-amber-100/40 dark:hover:bg-slate-700/40 transition-colors"
            >
              <Plus size={12} /> Add
            </button>
          )}
        </div>
      </div>
    );
  };

  const cell = 'min-h-0 border-slate-300/40 dark:border-slate-700/60';

  return (
    <div className="flex flex-col gap-4 h-[calc(100vh-9rem)] min-h-[560px]">
      {/* toolbar */}
      <div className="flex items-center justify-between flex-wrap gap-3 shrink-0">
        <div className="flex items-center gap-2">
          <button onClick={() => shiftWeek(-1)} className="p-2 rounded-lg bg-peach-100 dark:bg-peach-900/30 text-peach-600 hover:bg-peach-200 dark:hover:bg-peach-900/50 transition-colors">
            <ChevronLeft size={18} />
          </button>
          <button onClick={goToToday} className="px-4 py-2 text-sm font-semibold rounded-lg bg-gradient-to-r from-sky-400 to-lavender-500 text-white shadow-md hover:shadow-lg transition-shadow">
            Today
          </button>
          <button onClick={() => shiftWeek(1)} className="p-2 rounded-lg bg-peach-100 dark:bg-peach-900/30 text-peach-600 hover:bg-peach-200 dark:hover:bg-peach-900/50 transition-colors">
            <ChevronRight size={18} />
          </button>
          <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100 ml-2">
            {weekDays[0].toLocaleDateString('en-US', { month: 'long', day: 'numeric' })} –{' '}
            {weekDays[6].toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
          </h2>
        </div>
        <GlobalControls displayStyle={view} onDisplayStyleChange={setView} />
      </div>

      {/* paper agenda: fixed height, two facing pages */}
      <div className="agenda-page agenda-fold rounded-3xl shadow-xl flex-1 min-h-0 grid grid-cols-2">
        {/* left page: Mon / Tue / Wed */}
        <div className="grid grid-rows-3 min-h-0 divide-y divide-slate-300/40 dark:divide-slate-700/60">
          <div className={cell}>{renderDay(weekDays[0], 0)}</div>
          <div className={cell}>{renderDay(weekDays[1], 1)}</div>
          <div className={cell}>{renderDay(weekDays[2], 2)}</div>
        </div>
        {/* right page: Thu / Fri / (Sat | Sun) */}
        <div className="grid grid-rows-3 min-h-0 divide-y divide-slate-300/40 dark:divide-slate-700/60 border-l border-slate-300/50 dark:border-slate-700/70">
          <div className={cell}>{renderDay(weekDays[3], 3)}</div>
          <div className={cell}>{renderDay(weekDays[4], 4)}</div>
          <div className={`${cell} grid grid-cols-2 divide-x divide-slate-300/40 dark:divide-slate-700/60`}>
            <div className="min-h-0">{renderDay(weekDays[5], 5, true)}</div>
            <div className="min-h-0">{renderDay(weekDays[6], 6, true)}</div>
          </div>
        </div>
      </div>

      {/* topic legend — click a topic to show/hide it; expand ▸ to reach sub-topics */}
      <div className="flex flex-wrap justify-center items-center gap-2 shrink-0">
        {orderTopics(mockTopics)
          .filter(({ topic }) => chainOf(topic.id).slice(1).every((a) => expandedTopics.has(a)))
          .map(({ topic, depth }) => {
            const hidden = hiddenTopics.has(topic.id);
            const children = hasChildren(topic.id);
            return (
              <div key={topic.id} className="flex items-center" style={{ marginLeft: depth * 6 }}>
                {children ? (
                  <button
                    onClick={() => toggleExpanded(topic.id)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 px-0.5"
                    title={expandedTopics.has(topic.id) ? 'Collapse' : 'Expand sub-topics'}
                  >
                    <span className={`inline-block transition-transform ${expandedTopics.has(topic.id) ? 'rotate-90' : ''}`}>▸</span>
                  </button>
                ) : (
                  <span className="w-3.5" />
                )}
                <button
                  onClick={() => toggleHidden(topic.id)}
                  onDoubleClick={() => openElement('topics', topic.id)}
                  title={hidden ? 'Hidden — click to show' : 'Shown — click to hide'}
                  className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded-full border transition-all ${
                    hidden
                      ? 'border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-600 line-through opacity-60'
                      : 'border-transparent text-white'
                  }`}
                  style={hidden ? undefined : { backgroundColor: topic.color }}
                >
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: hidden ? topic.color : 'rgba(255,255,255,0.9)' }}
                  />
                  {topic.name}
                </button>
              </div>
            );
          })}
      </div>
    </div>
  );
}
