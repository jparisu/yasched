import { useState } from 'react';
import { Target, Clock, AlertCircle, CheckCircle2, ArrowRight, Zap, PenLine, Star, X, ChevronDown } from 'lucide-react';
import { DisplayItem, GlobalControls, PanelCard } from '../components/ui';
import { useCollapse } from '../lib/useCollapse';
import { useData } from '../data/DataContext';
import { useEditor } from '../data/EditorContext';
import { useElement } from '../data/ElementContext';
import { usePanelConfig } from '../data/usePanelConfig';
import { useSettings } from '../data/SettingsContext';
import { itemListClass } from '../lib/itemList';
import { levelOf } from '../lib/levels';
import { orderTasks, visibleDeadlines } from '../lib/tasks';
import { baseId, fetchEntity, updateEntity, EntityKind, EntitySpec } from '../api/client';

export function Focus() {
  const { tasks: mockTasks, events: mockEvents, deadlines: mockDeadlines, reload } = useData();
  const { view: displayStyle, setView } = usePanelConfig('focus');
  const { openEdit, canEdit } = useEditor();
  const { openElement } = useElement();
  const { settings } = useSettings();
  const [clearing, setClearing] = useState(false);
  const onFocusBlock = useCollapse('focus-onfocus');
  const notesBlock = useCollapse('focus-notes');

  // Everything the user has flagged "on focus" (tasks + de-duplicated events).
  const onFocusTasks = mockTasks.filter((t) => t.onFocus);
  const seenEv = new Set<string>();
  const onFocusEvents = mockEvents.filter((e) => {
    if (!e.onFocus) return false;
    const b = baseId(e.id);
    if (seenEv.has(b)) return false;
    seenEv.add(b);
    return true;
  });
  const focusCount = onFocusTasks.length + onFocusEvents.length;

  const clearOnFocus = async () => {
    setClearing(true);
    const jobs: [EntityKind, string][] = [
      ...onFocusTasks.map((t) => ['tasks', t.id] as [EntityKind, string]),
      ...onFocusEvents.map((e) => ['events', baseId(e.id)] as [EntityKind, string]),
    ];
    try {
      for (const [kind, id] of jobs) {
        const raw = await fetchEntity(kind, id);
        const attrs = raw.attributes;
        if (attrs && typeof attrs === 'object') delete (attrs as EntitySpec)['on-focus'];
        await updateEntity(kind, id, raw);
      }
      reload();
    } finally {
      setClearing(false);
    }
  };
  const highPriorityTasks = mockTasks
    .filter(t => levelOf(t.priority, settings.priorityRanges) === 'high' && t.status !== 'done')
    .slice(0, 3);

  const urgentDeadlines = visibleDeadlines(mockDeadlines, mockTasks)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .slice(0, 3);

  const upcomingEvents = mockEvents
    .filter(e => {
      const eventDate = new Date(e.date).toDateString();
      const today = new Date().toDateString();
      return eventDate === today || new Date(e.date) > new Date();
    })
    .slice(0, 3);

  const currentFocus = highPriorityTasks[0];

  return (
    <div className="max-w-5xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <div className="text-center flex-1 mb-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-lavender-100 to-sky-100 dark:from-lavender-900/30 dark:to-sky-900/30 text-lavender-600 dark:text-lavender-400 text-sm font-semibold mb-2">
            <Zap size={16} />
            Focus Mode
          </div>
          <h2 className="text-2xl font-bold text-slate-800 dark:text-slate-100">
            What should you work on now?
          </h2>
        </div>
        <GlobalControls displayStyle={displayStyle} onDisplayStyleChange={setView} />
      </div>

      {/* On-focus: the tasks/events the user flagged to keep in mind right now */}
      <div className="rounded-2xl p-4 border border-cyan-200 dark:border-cyan-800 bg-gradient-to-br from-cyan-50 to-sky-50 dark:from-cyan-900/20 dark:to-sky-900/10">
        <div className="flex items-center justify-between mb-3">
          <button onClick={onFocusBlock.toggle} className="flex items-center gap-2 font-semibold text-slate-800 dark:text-slate-100">
            <ChevronDown size={16} className={`text-cyan-500 transition-transform ${onFocusBlock.collapsed ? '-rotate-90' : ''}`} />
            <Star size={16} className="text-cyan-500" /> On Focus
            <span className="text-xs font-normal text-slate-400">({focusCount})</span>
          </button>
          {canEdit && focusCount > 0 && !onFocusBlock.collapsed && (
            <button
              onClick={clearOnFocus}
              disabled={clearing}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-cyan-700 dark:text-cyan-300 bg-white dark:bg-slate-800 border border-cyan-200 dark:border-cyan-700 hover:bg-cyan-100 dark:hover:bg-cyan-900/40 disabled:opacity-50"
            >
              <X size={14} /> {clearing ? 'Clearing…' : 'Clear on-focus'}
            </button>
          )}
        </div>
        {onFocusBlock.collapsed ? null : focusCount === 0 ? (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Nothing on focus yet. Open any task or event and tick <span className="font-medium">“On focus”</span> at the top of its panel.
          </p>
        ) : (
          <div className={itemListClass(displayStyle)}>
            {orderTasks(onFocusTasks).map(({ task, depth }) => (
              <DisplayItem
                key={task.id}
                title={task.title}
                displayStyle={displayStyle}
                itemStyle={task.style}
                priority={task.priority}
                status={task.status}
                deadline={task.deadline}
                depth={depth}
                onClick={() => openEdit('tasks', task.id)}
                onDoubleClick={() => openElement('tasks', task.id)}
              />
            ))}
            {onFocusEvents.map((event) => (
              <DisplayItem
                key={event.id}
                title={event.title}
                displayStyle={displayStyle}
                itemStyle={event.style}
                startTime={event.startTime}
                endTime={event.endTime}
                recurring={event.recurring}
                onClick={() => openEdit('events', baseId(event.id))}
                onDoubleClick={() => openElement('events', baseId(event.id))}
              />
            ))}
          </div>
        )}
      </div>

      {currentFocus && (
        <div className="rounded-2xl p-6 bg-gradient-to-br from-sky-100 via-lavender-50 to-mint-50 dark:from-sky-900/30 dark:via-lavender-900/20 dark:to-mint-900/10 border-2 border-sky-200 dark:border-sky-800 shadow-lg">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-sky-400 to-lavender-500 flex items-center justify-center text-white flex-shrink-0 shadow-lg">
              <Target size={28} />
            </div>
            <div className="flex-1">
              <p className="text-xs font-bold text-sky-600 dark:text-sky-400 uppercase tracking-wide mb-1">
                Current Focus
              </p>
              <h3 className="text-2xl font-bold text-slate-800 dark:text-slate-100 mb-2">
                {currentFocus.title}
              </h3>
              {currentFocus.description && (
                <p className="text-slate-600 dark:text-slate-300 mb-3">
                  {currentFocus.description}
                </p>
              )}
              <div className="flex items-center gap-3 flex-wrap">
                <span className="inline-flex items-center gap-1.5 text-sm bg-coral-100 dark:bg-coral-900/30 px-3 py-1.5 rounded-full text-coral-600 dark:text-coral-400 font-medium">
                  <AlertCircle size={14} />
                  High Priority
                </span>
                {currentFocus.deadline && (
                  <span className="inline-flex items-center gap-1.5 text-sm bg-white dark:bg-slate-800 px-3 py-1.5 rounded-full text-slate-600 dark:text-slate-300">
                    <Clock size={14} />
                    Due {new Date(currentFocus.deadline).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </span>
                )}
              </div>
            </div>
            <button className="px-5 py-2.5 bg-gradient-to-r from-sky-400 to-lavender-500 hover:from-sky-500 hover:to-lavender-600 text-white rounded-xl font-semibold transition-all shadow-md hover:shadow-lg flex items-center gap-2">
              Start <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <PanelCard title="Priority Tasks" subtitle="High priority items" colorClass="sky" variant="colorful">
          <div className={itemListClass(displayStyle)}>
            {highPriorityTasks.length > 0 ? (
              orderTasks(highPriorityTasks).map(({ task, depth }) => (
                <DisplayItem
                  key={task.id}
                  title={task.title}
                  description={task.description}
                  displayStyle={displayStyle}
                  itemStyle={task.style}
                  topicId={task.topicId}
                  priority={task.priority}
                  deadline={task.deadline}
                  depth={depth}
                  onClick={() => openEdit('tasks', baseId(task.id))}
                  onDoubleClick={() => openElement('tasks', baseId(task.id))}
                />
              ))
            ) : (
              <div className="py-8 text-center">
                <CheckCircle2 className="w-12 h-12 mx-auto text-mint-500 mb-2" />
                <p className="text-slate-500 dark:text-slate-400 text-sm">
                  All high priority tasks completed
                </p>
              </div>
            )}
          </div>
        </PanelCard>

        <PanelCard title="Close Deadlines" subtitle="Approaching due dates" colorClass="coral" variant="colorful">
          <div className={itemListClass(displayStyle)}>
            {urgentDeadlines.map((deadline) => (
              <DisplayItem
                key={deadline.id}
                title={deadline.title}
                displayStyle={displayStyle}
                itemStyle={deadline.style}
                topicId={deadline.topicId}
                priority={deadline.priority}
                deadline={deadline.date}
                onClick={() => openEdit('tasks', baseId(deadline.id))}
                onDoubleClick={() => openElement('tasks', baseId(deadline.id))}
              />
            ))}
          </div>
        </PanelCard>

        <PanelCard title="Today's Events" subtitle="Upcoming schedule" colorClass="lavender" variant="colorful">
          <div className={itemListClass(displayStyle)}>
            {upcomingEvents.map((event) => (
              <DisplayItem
                key={event.id}
                title={event.title}
                displayStyle={displayStyle}
                itemStyle={event.style}
                topicId={event.topicId}
                startTime={event.startTime}
                endTime={event.endTime}
                recurring={event.recurring}
                onClick={() => openEdit('events', baseId(event.id))}
                onDoubleClick={() => openElement('events', baseId(event.id))}
              />
            ))}
          </div>
        </PanelCard>
      </div>

      <div className="rounded-2xl p-4 bg-gradient-to-br from-peach-50 to-lemon-50 dark:from-peach-900/20 dark:to-lemon-900/20 border border-peach-200 dark:border-peach-800">
        <button onClick={notesBlock.toggle} className="flex items-center gap-2 mb-3">
          <ChevronDown size={16} className={`text-peach-600 transition-transform ${notesBlock.collapsed ? '-rotate-90' : ''}`} />
          <PenLine size={16} className="text-peach-600" />
          <h4 className="font-semibold text-slate-800 dark:text-slate-100">Notes</h4>
        </button>
        {!notesBlock.collapsed && (
          <textarea
            className="w-full h-24 p-3 rounded-xl bg-white/80 dark:bg-slate-800/80 border border-peach-200 dark:border-peach-800 text-slate-800 dark:text-slate-100 resize-none focus:outline-none focus:ring-2 focus:ring-peach-400 font-sans"
            placeholder="Add notes for your focus session..."
          />
        )}
      </div>
    </div>
  );
}
